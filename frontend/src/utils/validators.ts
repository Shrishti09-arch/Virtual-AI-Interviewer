export const isValidEmail = (email: string): boolean => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const validateFileSize = (file: File, maxMb = 10): { valid: boolean; error?: string } => {
  const maxBytes = maxMb * 1024 * 1024;
  if (file.size > maxBytes) {
    return {
      valid: false,
      error: `File size exceeds maximum allowed limit of ${maxMb}MB.`,
    };
  }
  return { valid: true };
};

export const isValidResumeExtension = (filename: string): boolean => {
  const lower = filename.toLowerCase();
  return lower.endsWith('.pdf') || lower.endsWith('.docx') || lower.endsWith('.doc') || lower.endsWith('.txt');
};
