export function logError(context, err) {
  console.error(`❌ [${context}]`, err);
  // Optionally: showToast("Upload failed!", "error")
}
