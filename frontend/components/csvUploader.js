import { parseCSV } from "../utils/parseCSV.js";
import { sendDataToAPI } from "../services/apiClient.js";
import { renderTable } from "./tableManager.js";
import { logError } from "../utils/errorHandler.js";
import { config } from "../config/appConfig.js";

export function setupCSVUploader() {
  const input = document.getElementById(config.inputId);
  if (!input) return logError("Uploader", `Missing input element: ${config.inputId}`);

  input.addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      const parsed = await parseCSV(file);
      const transformed = await sendDataToAPI(parsed, config.apiUrl);
      renderTable(transformed, config.outputId);
    } catch (err) {
      logError("CSV Upload Flow", err);
    }
  });
}
