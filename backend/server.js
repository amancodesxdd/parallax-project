const PDFDocument = require("pdfkit");
const express = require("express");
const cors = require("cors");
const { PrismaClient } = require("@prisma/client");
const { calculateRiskScore } = require("./rules");

// Initialize Express app & Prisma Client
const app = express();
const prisma = new PrismaClient();

// Middleware
app.use(cors());
app.use(express.json());

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
    // 2. Risk Engine Calculation (rules.js)
    const { riskScore, verdict, flags } = calculateRiskScore({
      documentNumber,
      expiryDate,
      dob,
      gender,
      nationality,
      faceScore: parseFloat(faceScore || 1.0),
      isBlacklisted
    });

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
        tamperingFlags: flags,
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
// Start listening on Port 5000
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 Passport Verification API running on http://localhost:${PORT}`);
});

// GET ENDPOINT: Fetch all scan records (Scan History)
app.get("/api/scans", async (req, res) => {
  try {
    const scans = await prisma.scan.findMany({
      orderBy: { createdAt: "desc" },
      take: 50 // Limit to latest 50 scans
    });
    res.json({ success: true, data: scans });
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