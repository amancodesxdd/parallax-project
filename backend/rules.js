// ==========================================
// STEP 4: INDIVIDUAL VALIDATION RULES
// ==========================================

// 1. Indian Passport Format Check (2 letters + 7 digits, e.g., AB1234567)
function validatePassportNumber(docNum) {
  if (!docNum) return false;
  const indianPassportRegex = /^[A-Z]{2}\d{7}$/;
  return indianPassportRegex.test(docNum.trim());
}

// 2. Expiration Date Check (Must be in the future)
function validateExpiryDate(expiryDate) {
  if (!expiryDate) return false;
  const expiry = new Date(expiryDate);
  const today = new Date();
  return expiry > today;
}

// 3. Date of Birth Check (Must be at least 18 years old)
function validateDOB(dob) {
  if (!dob) return false;
  const birthDate = new Date(dob);
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  return age >= 18;
}

// 4. Gender Code Check (M, F, X)
function validateGender(gender) {
  if (!gender) return false;
  const validGenders = ["M", "F", "X"];
  return validGenders.includes(gender.toUpperCase());
}

// 5. Nationality Code Check (IND)
function validateNationality(nationality) {
  if (!nationality) return false;
  return nationality.toUpperCase() === "IND";
}

// ==========================================
// STEPS 6 & 7: RISK ENGINE & VERDICT LOGIC
// ==========================================

function calculateRiskScore({ documentNumber, expiryDate, dob, gender, nationality, faceScore, isBlacklisted }) {
  let validationErrors = 0;
  let tamperingFlagsCount = 0;
  let faceMismatchScore = 0;
  const flags = [];

  // --- Category 1: Validation Rules (40% Weight Category) ---
  if (!validatePassportNumber(documentNumber)) {
    validationErrors += 20;
    flags.push("INVALID_PASSPORT_FORMAT");
  }

  if (!validateExpiryDate(expiryDate)) {
    validationErrors += 20;
    flags.push("EXPIRED_DOCUMENT");
  }

  if (!validateDOB(dob)) {
    validationErrors += 20;
    flags.push("UNDERAGE_OR_INVALID_DOB");
  }

  if (!validateGender(gender)) {
    validationErrors += 20;
    flags.push("INVALID_GENDER_CODE");
  }

  if (!validateNationality(nationality)) {
    validationErrors += 20;
    flags.push("UNSUPPORTED_NATIONALITY");
  }

  // --- Category 2: Blacklist Check (40% Weight Category) ---
  if (isBlacklisted) {
    tamperingFlagsCount += 100;
    flags.push("BLACKLISTED_DOCUMENT");
  }

  // --- Category 3: Face Score Check (20% Weight Category) ---
  const parsedFaceScore = parseFloat(faceScore) || 1.0;
  if (parsedFaceScore < 0.75) {
    faceMismatchScore = (1 - parsedFaceScore) * 100;
    flags.push("LOW_FACE_MATCH_SCORE");
  }

  // --- Weighted Risk Calculation Formula ---
  // (Validation Errors × 40%) + (Tampering/Blacklist × 40%) + (Face Mismatch × 20%)
  const rawScore = 
    (Math.min(validationErrors, 100) * 0.40) +
    (Math.min(tamperingFlagsCount, 100) * 0.40) +
    (Math.min(faceMismatchScore, 100) * 0.20);

  const finalRiskScore = Math.round(Math.min(rawScore, 100));

  // --- Step 7: Verdict Assignment Logic ---
  // 0-30: APPROVE, 31-60: REVIEW, 61-100: REJECT
  let verdict = "APPROVE";
  if (finalRiskScore > 60) {
    verdict = "REJECT";
  } else if (finalRiskScore >= 31) {
    verdict = "REVIEW";
  }

  return { riskScore: finalRiskScore, verdict, flags };
}

module.exports = {
  validatePassportNumber,
  validateExpiryDate,
  validateDOB,
  validateGender,
  validateNationality,
  calculateRiskScore
};