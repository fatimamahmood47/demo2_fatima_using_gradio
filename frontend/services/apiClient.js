export async function sendDataToAPI(data, apiUrl) {
  const response = await fetch(apiUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Server responded with ${response.status}: ${errorText}`);
  }

  return await response.json();
}
