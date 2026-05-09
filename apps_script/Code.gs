function doGet() {
  return HtmlService.createHtmlOutputFromFile('index')
    .setTitle('X投稿ネタ登録')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function addPosts(postsText) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  const lines = postsText.split('\n').filter(line => line.trim() !== '');
  if (lines.length === 0) return 0;

  const lastRow = sheet.getLastRow();

  let nextId = 1;
  if (lastRow > 1) {
    const lastId = sheet.getRange(lastRow, 1).getValue();
    nextId = (parseInt(lastId) || 0) + 1;
  }

  let nextDate = new Date();
  nextDate.setDate(nextDate.getDate() + 1);

  if (lastRow > 1) {
    const dateValues = sheet.getRange(2, 3, lastRow - 1, 1).getValues();
    let maxDate = new Date(0);
    for (const row of dateValues) {
      if (row[0]) {
        const d = new Date(row[0]);
        if (!isNaN(d) && d > maxDate) maxDate = d;
      }
    }
    if (maxDate > nextDate) {
      nextDate = new Date(maxDate);
      nextDate.setDate(nextDate.getDate() + 1);
    }
  }

  const rows = [];
  for (let i = 0; i < lines.length; i++) {
    const text = lines[i].trim();
    if (!text) continue;
    const dateStr = Utilities.formatDate(nextDate, 'Asia/Tokyo', 'yyyy-MM-dd');
    rows.push([nextId + i, text, dateStr, 'FALSE']);
    nextDate.setDate(nextDate.getDate() + 1);
  }

  if (rows.length > 0) {
    sheet.getRange(lastRow + 1, 1, rows.length, 4).setValues(rows);
  }

  return rows.length;
}
