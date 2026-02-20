/**
 * Axlow Lead Hunter — Google Apps Script Webhook
 * Paste this into Extensions > Apps Script in the Axlow Leads sheet.
 * Deploy as Web App: Execute as "Me", access "Anyone".
 * Copy the deployment URL and send it back.
 */

const HEADERS = [
  "first_name","last_name","email","company","title",
  "linkedin_url","location","company_type","company_size",
  "icp_tier","priority_score","priority_level","sequence",
  "personalization_line","hook_angle","email_source",
  "pain_signals","company_context","date_added","date_verified",
  "status","notes"
];

function doPost(e) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

    // Write header row if sheet is empty
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(HEADERS);
      sheet.getRange(1, 1, 1, HEADERS.length).setBackground("#1D4740").setFontColor("#FFFFFF").setFontWeight("bold");
      sheet.setFrozenRows(1);
    }

    const payload = JSON.parse(e.postData.contents);

    // ── UPDATE PERSONALIZATION ACTION ──────────────────────────────
    if (payload.action === "update_personalization") {
      const rows  = payload.rows || [];
      const data  = sheet.getDataRange().getValues();
      const eCol  = HEADERS.indexOf("email") + 1;
      const pCol  = HEADERS.indexOf("personalization_line") + 1;
      let updated = 0;
      for (const update of rows) {
        const email = (update.email || "").toLowerCase();
        for (let i = 1; i < data.length; i++) {
          if ((data[i][eCol-1]||"").toLowerCase() === email) {
            sheet.getRange(i+1, pCol).setValue(update.personalization_line || "");
            updated++;
            break;
          }
        }
      }
      return ContentService
        .createTextOutput(JSON.stringify({ ok: true, updated }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    const leads   = Array.isArray(payload) ? payload : [payload];
    const added   = [];

    // Load existing emails + linkedin URLs for deduplication
    const existing = new Set();
    const data = sheet.getDataRange().getValues();
    const emailCol   = HEADERS.indexOf("email");
    const linkedinCol = HEADERS.indexOf("linkedin_url");
    for (let i = 1; i < data.length; i++) {
      if (data[i][emailCol])    existing.add(data[i][emailCol].toLowerCase());
      if (data[i][linkedinCol]) existing.add(data[i][linkedinCol].toLowerCase());
    }

    for (const lead of leads) {
      const email   = (lead.email   || "").toLowerCase();
      const linkedin = (lead.linkedin_url || "").toLowerCase();
      if ((email && existing.has(email)) || (linkedin && existing.has(linkedin))) continue;

      const row = HEADERS.map(h => lead[h] || "");
      sheet.appendRow(row);

      // Color-code priority level
      const lastRow = sheet.getLastRow();
      const priority = lead.priority_level || "";
      if (priority === "A") {
        sheet.getRange(lastRow, 1, 1, HEADERS.length).setBackground("#E8F4F0");
      }

      existing.add(email);
      if (linkedin) existing.add(linkedin);
      added.push(lead);
    }

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true, added: added.length, skipped: leads.length - added.length }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch(err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  return ContentService
    .createTextOutput(JSON.stringify({ ok: true, rows: sheet.getLastRow() - 1, status: "Axlow Lead Hunter webhook ready" }))
    .setMimeType(ContentService.MimeType.JSON);
}
