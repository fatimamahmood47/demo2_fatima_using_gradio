let tableInstance = null;

export function renderTable(data, containerId) {
  tableInstance = new Tabulator(`#${containerId}`, {
    data,
    layout: "fitColumns",
    columns: Object.keys(data[0] || {}).map(key => ({
      title: key,
      field: key,
      editor: "input"
    }))
  });

  tableInstance.on("cellEdited", (cell) => {
    console.log("✏️ Cell edited:", cell.getField(), cell.getOldValue(), "→", cell.getValue());
  });
}

export function exportTable() {
  if (tableInstance) {
    tableInstance.download("csv", "edited_table_data.csv");
  }
}
