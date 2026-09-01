const PDFDocument = require("pdfkit");
const express = require("express");
const cors = require("cors");
const fs = require("fs");
const path = require("path");
const multer = require("multer");
const { exec } = require("child_process");
const { promisify } = require("util");
const { PrismaClient } = require("@prisma/client");
const { calculateRiskScore } = require("./rules");

require("dotenv").config();

const execPromise = promisify(exec);

// Multer setup: accepts images + PDFs up to 10MB, stored in backend/uploads/
const UPLOAD_DIR = path.join(__dirname, "uploads");
fs.mkdirSync(UPLOAD_DIR, { recursive: true });

const allowedExtensions = [".jpg", ".jpeg", ".png", ".webp", ".pdf"];
const upload = multer({
  storage: multer.diskStorage({
    destination: (req, file, cb) => cb(null, UPLOAD_DIR),
    filename: (req, file, cb) => {
      const ext = (path.extname(file.originalname || "") || ".bin").toLowerCase();
      cb(null, `${Date.now()}-${Math.random().toString(16).slice(2)}${ext}`);
    }
  }),
  limits: { fileSize: 10 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    const ext = path.extname(file.originalname || "").toLowerCase();
    if (allowedExtensions.includes(ext)) cb(null, true);
    else cb(new Error(`Unsupported file type '${ext}'. Allowed: ${allowedExtensions.join(", ")}`));
  }
});

const forensicsPython = () => process.env.FORENSICS_PYTHON || "python";

// Initialize Express app & Prisma Client
const app = express();
const prisma = new PrismaClient();

// Middleware
app.use(cors());
app.use(express.json());
app.use("/uploads", express.static(UPLOAD_DIR, { maxAge: "7d" }));

// Main Verification Endpoint
app.post("/api/scan", async (req, res) => {
  try {
    const { 
      documentType, 
      documentNumber, 
      expiryDate, 
      dob, 
      gender, 
      nationality, 
      faceScore, 
      extractedData 
    } = req.body;


    // 1. Safe Blacklist Check (Supabase Database Lookup)
    const blacklisted = documentNumber 
      ? await prisma.blacklist.findFirst({
          where: { documentNumber: String(documentNumber) }
        })
      : null;
      
    const isBlacklisted = !!blacklisted;

    // 1.5 Forensic Checks (AI-generation + tampering via Python engine) when an image path is supplied
    const forensicFlags = [];
    let forensicScore = 0;
    if (req.body.imagePath) {
      const [aiResult, tamperResult] = await Promise.all([
        runAiDetection(req.body.imagePath),
        runTamperDetection(req.body.imagePath)
      ]);

      if (aiResult.isAiGenerated) {
        forensicScore += aiResult.aiScore || 0;
        forensicFlags.push(...(aiResult.flags || []));
      }
      if (tamperResult.isTampered) {
        forensicScore += tamperResult.tamperScore || 0;
        forensicFlags.push(...(tamperResult.flags || []));
      }
    }

    // 2. Risk Engine Calculation (rules.js)
    const { riskScore, verdict, flags } = calculateRiskScore({
      documentNumber,
      expiryDate,
      dob,
      gender,
      nationality,
      faceScore: parseFloat(faceScore || 1.0),
      isBlacklisted,
      tamperScore: forensicScore
    });
    const allFlags = [...flags, ...forensicFlags];

    // 3. Save Audit Log to Supabase Scan Table
    const scanRecord = await prisma.scan.create({
      data: {
        documentType: documentType || "PASSPORT",
        extractedData: extractedData || { documentNumber, expiryDate, dob, gender, nationality },
        validationResults: { 
          isBlacklisted, 
          passportFormatValid: !flags.includes("INVALID_PASSPORT_FORMAT"),
          isExpired: flags.includes("EXPIRED_DOCUMENT")
        },
        tamperingFlags: allFlags,
        faceScore: parseFloat(faceScore || 1.0),
        riskScore: parseFloat(riskScore),
        verdict: verdict
      }
    });

    // 4. Return Final Response
    res.status(201).json({
      success: true,
      data: scanRecord
    });

  } catch (error) {
    console.error("Error processing scan:", error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// POST /api/scan/file - single-call multipart scan for the frontend.
// Accepts a document image (required) + optional selfie + optional field overrides,
// runs the full Python forensic pipeline (OCR + AI + tamper + face), then scores it.
app.post("/api/scan/file",
  upload.fields([{ name: "document", maxCount: 1 }, { name: "selfie", maxCount: 1 }]),
  async (req, res) => {
    try {
      if (!req.files?.document?.[0]) {
        return res.status(400).json({ success: false, error: "document file is required (multipart field 'document')" });
      }

      const docPath = req.files.document[0].path;
      const selfiePath = req.files.selfie?.[0]?.path || null;
      const body = req.body || {};

      // 1. Single Python forensics pass: OCR + AI + tamper + face
      const selfieArg = selfiePath ? ` --selfie "${selfiePath}"` : "";
      const { stdout } = await execPromise(
        `${forensicsPython()} forensics_pipeline.py --document "${docPath}"${selfieArg}`
      );
      const forensics = JSON.parse(stdout);

      // 2. Merge OCR-extracted fields with explicit client overrides
      const ocrFields = forensics.ocr?.fields || {};
      const documentNumber = body.documentNumber || ocrFields.DocumentNumber?.value;
      const expiryDate = body.expiryDate || ocrFields.DateOfExpiration?.value;
      const dob = body.dob || ocrFields.DateOfBirth?.value;
      const gender = body.gender;
      const nationality = body.nationality || ocrFields.CountryRegion?.value;
      const extractedData = { documentNumber, expiryDate, dob, gender, nationality };

      // 3. Blacklist lookup (Supabase)
      const blacklisted = documentNumber
        ? await prisma.blacklist.findFirst({ where: { documentNumber: String(documentNumber) } })
        : null;
      const isBlacklisted = !!blacklisted;

      // 4. Risk engine (face + tamper scores from the Python pipeline)
      const faceScoreFraction = typeof forensics.face?.face_score === "number"
        ? forensics.face.face_score / 100
        : 1.0;

      const { riskScore, verdict, flags } = calculateRiskScore({
        documentNumber,
        expiryDate,
        dob,
        gender,
        nationality,
        faceScore: faceScoreFraction,
        isBlacklisted,
        tamperScore: (forensics.tamper?.tamperScore || 0) + (forensics.ai?.aiScore || 0)
      });

      const forensicFlagList = [
        ...(forensics.tamper?.flags || []),
        ...(forensics.ai?.flags || [])
      ];
      const allFlags = [...new Set([...flags, ...forensicFlagList])];

      // 5. Persist audit record
      const scanRecord = await prisma.scan.create({
        data: {
          documentType: body.documentType || "PASSPORT",
          extractedData,
          validationResults: {
            isBlacklisted,
            passportFormatValid: !flags.includes("INVALID_PASSPORT_FORMAT"),
            isExpired: flags.includes("EXPIRED_DOCUMENT")
          },
          tamperingFlags: allFlags,
          faceScore: faceScoreFraction,
          riskScore: parseFloat(riskScore),
          verdict: verdict
        }
      });

      // 6. Return verdict + full forensic breakdown
      const evidenceImageUrl = forensics.annotatedImagePath
        ? `/uploads/${path.basename(forensics.annotatedImagePath)}`
        : null;

      res.status(201).json({
        success: true,
        message: "Document screening completed successfully",
        data: {
          id: scanRecord.id,
          verdict,
          riskScore: parseFloat(riskScore),
          faceScore: faceScoreFraction,
          extractedData,
          tamperingFlags: allFlags,
          evidenceImageUrl,
          forensics: {
            ocr: forensics.ocr,
            ai: forensics.ai,
            tamper: forensics.tamper,
            face: forensics.face
          }
        }
      });
    } catch (error) {
      console.error("Error processing file scan:", error);
      res.status(500).json({ success: false, error: error.message });
    }
  }
);

// Multer/validation error handler
// eslint-disable-next-line no-unused-vars
app.use((err, req, res, next) => {
  res.status(400).json({ success: false, error: err.message });
});
// GET ENDPOINT: Generate and download a PDF Verification Certificate
// GET ENDPOINT: Generate and download a PDF Verification Certificate
app.get("/api/scans/:id/pdf", async (req, res) => {
  try {
    const scan = await prisma.scan.findUnique({
      where: { id: req.params.id }
    });

    if (!scan) {
      return res.status(404).json({ success: false, error: "Scan record not found" });
    }

    const doc = new PDFDocument({ margin: 50 });

    // FORCE DIRECT DOWNLOAD TO PC (attachment instead of inline)
    res.setHeader("Content-Type", "application/pdf");
    res.setHeader(
      "Content-Disposition", 
      `attachment; filename="passport_audit_${scan.id}.pdf"`
    );

    doc.pipe(res);

    // Document Header
    doc.fontSize(20).text("PASSPORT VERIFICATION AUDIT CERTIFICATE", { align: "center" });
    doc.moveDown();
    doc.fontSize(10).text(`Generated: ${new Date().toISOString()}`, { align: "right" });
    doc.moveDown();

    // Verification Summary
    doc.fontSize(14).text("1. Scan Summary", { underline: true });
    doc.fontSize(10).text(`Scan ID: ${scan.id}`);
    doc.text(`Document Type: ${scan.documentType}`);
    doc.text(`Verdict: ${scan.verdict}`);
    doc.text(`Risk Score: ${scan.riskScore} / 100`);
    doc.text(`Face Match Score: ${(scan.faceScore * 100).toFixed(1)}%`);
    doc.moveDown();

    // Validation & Tampering Flags
    doc.fontSize(14).text("2. Verification Flags", { underline: true });
    const flags = scan.tamperingFlags.length > 0 ? scan.tamperingFlags.join(", ") : "NONE (CLEAN SCAN)";
    doc.fontSize(10).text(`Flags Triggered: ${flags}`);
    doc.moveDown();

    // Extracted Passport Details
    doc.fontSize(14).text("3. Extracted Document Details", { underline: true });
    doc.fontSize(10).text(JSON.stringify(scan.extractedData, null, 2));

    doc.end();
  } catch (error) {
    console.error("PDF Generation Error:", error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /health - System Uptime & Dependency Status
app.get("/health", async (req, res) => {
  const healthStatus = {
    status: "UP",
    timestamp: new Date().toISOString(),
    services: {
      database: "UNKNOWN",
      pythonEngine: "UNKNOWN"
    }
  };

  // 1. Check PostgreSQL Database Connection via Prisma
  try {
    await prisma.$queryRaw`SELECT 1`;
    healthStatus.services.database = "CONNECTED";
  } catch (err) {
    healthStatus.services.database = "DISCONNECTED";
    healthStatus.status = "DEGRADED";
  }

  // 2. Check Python Environment
  try {
    await execPromise("python --version");
    healthStatus.services.pythonEngine = "AVAILABLE";
  } catch (err) {
    healthStatus.services.pythonEngine = "UNAVAILABLE";
    healthStatus.status = "DEGRADED";
  }

  const httpCode = healthStatus.status === "UP" ? 200 : 503;
  res.status(httpCode).json(healthStatus);
});

// Start listening on Port 5000 (or the port provided via PORT)
const PORT = process.env.PORT || 5000;
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`🚀 Passport Verification API running on http://localhost:${PORT}`);
  });
}

module.exports = app;

// GET ENDPOINT: Fetch all scan records (Scan History) with status filter + pagination
app.get("/api/scans", async (req, res) => {
  try {
    const page = Math.max(parseInt(req.query.page, 10) || 1, 1);
    const limit = Math.min(Math.max(parseInt(req.query.limit, 10) || 50, 1), 100);
    const skip = (page - 1) * limit;
    const where = req.query.status ? { verdict: String(req.query.status).toUpperCase() } : {};

    const [total, scans] = await Promise.all([
      prisma.scan.count({ where }),
      prisma.scan.findMany({
        where,
        orderBy: { createdAt: "desc" },
        take: limit,
        skip
      })
    ]);

    res.json({
      success: true,
      pagination: {
        total,
        page,
        limit,
        pages: Math.max(1, Math.ceil(total / limit))
      },
      data: scans
    });
  } catch (error) {
    console.error("Error fetching scans:", error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET ENDPOINT: System Analytics & Verdict Totals
app.get("/api/stats", async (req, res) => {
  try {
    const totalScans = await prisma.scan.count();
    const approved = await prisma.scan.count({ where: { verdict: "APPROVE" } });
    const review = await prisma.scan.count({ where: { verdict: "REVIEW" } });
    const rejected = await prisma.scan.count({ where: { verdict: "REJECT" } });

    res.json({
      success: true,
      data: {
        totalScans,
        approved,
        review,
        rejected
      }
    });
  } catch (error) {
    console.error("Error fetching stats:", error);
    res.status(500).json({ success: false, error: error.message });
  }
});
// Call Python forensic engine: AI-generation detection
async function runAiDetection(imagePath) {
  if (!imagePath) return { aiScore: 0, isAiGenerated: false, flags: [] };
  try {
    const { stdout } = await execPromise(`${forensicsPython()} ai_detector.py "${imagePath}"`);
    return JSON.parse(stdout);
  } catch (error) {
    console.error("AI Detection Execution Error:", error);
    return { aiScore: 0, isAiGenerated: false, flags: ["AI_DETECTION_FAILED"] };
  }
}

// Call Python forensic engine: tampering/photo-cut detection
async function runTamperDetection(imagePath) {
  if (!imagePath) return { tamperScore: 0, isTampered: false, flags: [], highlightedImagePath: null };
  try {
    const { stdout } = await execPromise(`${forensicsPython()} tamper_detector.py "${imagePath}"`);
    return JSON.parse(stdout);
  } catch (error) {
    console.error("Tamper Detection Execution Error:", error);
    return { tamperScore: 0, isTampered: false, flags: ["TAMPER_DETECTION_FAILED"], highlightedImagePath: null };
  }
}