const http = require("http");

function sendScanRequest(payload, scenarioName) {
  const data = JSON.stringify(payload);

  const req = http.request(
    "http://localhost:5000/api/scan",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(data),
      },
    },
    (res) => {
      let body = "";
      res.on("data", (chunk) => (body += chunk));
      res.on("end", () => {
        console.log(`\n=== ${scenarioName} ===`);
        console.log("Status Code:", res.statusCode);
        console.log("Response:", JSON.parse(body));
      });
    }
  );

  req.on("error", (err) => {
    console.error(`Error in ${scenarioName}:`, err.message);
  });

  req.write(data);
  req.end();
}

// 1. Test Valid Passport
sendScanRequest(
  {
    documentType: "PASSPORT",
    documentNumber: "AB1234567",
    expiryDate: "2030-01-01",
    dob: "1995-05-20",
    gender: "M",
    nationality: "IND",
    faceScore: 0.95,
  },
  "TEST 1: Valid Passport"
);

const http = require("http");

const payload = JSON.stringify({
  documentType: "PASSPORT",
  documentNumber: "AB1234567",
  expiryDate: "2030-01-01",
  dob: "1995-05-20",
  gender: "M",
  nationality: "IND",
  faceScore: 0.95
});

const req = http.request(
  "http://localhost:5000/api/scan",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Content-Length": Buffer.byteLength(payload)
    }
  },
  (res) => {
    let body = "";
    res.on("data", (chunk) => (body += chunk));
    res.on("end", () => {
      console.log("\n=== TEST RESPONSE ===");
      console.log("Status:", res.statusCode);
      console.log("Payload:", JSON.parse(body));
    });
  }
);

req.on("error", (err) => {
  console.error("Test Request Failed:", err.message);
});

req.write(payload);
req.end();