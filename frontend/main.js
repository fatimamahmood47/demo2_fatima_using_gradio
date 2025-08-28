import { setupCSVUploader } from "./components/csvUploader.js";
import { exportTable } from "./components/tableManager.js";
import { config } from "./config/appConfig.js";

document.addEventListener("DOMContentLoaded", () => {
  setupCSVUploader();

  document.getElementById(config.exportBtnId)?.addEventListener("click", exportTable);
});
