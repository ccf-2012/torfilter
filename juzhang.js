// ==UserScript==
// @name         局长保种下载
// @namespace    https://greasyfork.org/zh-CN/scripts/
// @version      0.1
// @license      GPL-3.0 License
// @description  Love from juzhang
// @author       ccf2012
// @icon         https://pterclub.com/favicon.ico
// @match        https://pterclub.com/viewclaims.php*
// @require      https://code.jquery.com/jquery-3.6.0.min.js
// @grant        GM_setClipboard
// @grant        GM.xmlHttpRequest

// ==/UserScript==

function addDownloadPanel() {
  var torTable = $("#outer > table");
  if (torTable.length <= 0) {
    return;
  }
  var donwnloadPanel = `
    <table align='center'> <tr>
    <td style='width: 80px; border: none;'>
        <button type="button" id="btn-copydllink" style="margin-top: 5px;margin-bottom: 5px;margin-left: 5px;">
        拷贝链接
        </button>
    </td>
    <td style='width: 220px; border: none;'> <div id="process-log" style="margin-left: 5px;"></div> </td>
    </tr>
    </table>
`;
  torTable.before(donwnloadPanel);
}

const pter_passkey = async () => {
  let html = await $.get("usercp.php");
  let passkeyRow = $(html).find('tr:contains("密钥"):last');
  if (passkeyRow.length > 0) {
    var key = passkeyRow.find("td:last").text();
    return "&passkey=" + key.trim();
  }
  return "";
};

function genDownloadLink(link, passKeyStr) {
  return link + passKeyStr;
}

var asyncCopyLink = async (html) => {
  $("#process-log").text("处理中...");
  let passKeyStr = await pter_passkey();
  // console.log(passKeyStr);

  let torlist = $(html).find(
    "#outer > table > tbody > tr > td > table > tbody > tr "
  );
  var resulttext = "";
  for (let index = 1; index < torlist.length; ++index) {
    if ($(torlist[index]).is(":visible")) {
      let hrefele = $(torlist[index]).find("td:nth-child(5) > a");
      if (hrefele.length > 0) {
        let dllinktemp = hrefele
          .prop("href")
          .replace("details.php", "download.php");
        let dllink = genDownloadLink(dllinktemp, passKeyStr);
        resulttext += dllink + "\n";
      }
    }
  }
  GM_setClipboard(resulttext, "text");
  $("#process-log").text("下载链接 已拷贝在剪贴板中");
};

function onClickCopyDownloadLink(html) {
  asyncCopyLink(html);
}

(function () {
  "use strict";

  addDownloadPanel(document);
  $("#btn-copydllink").click(function () {
    onClickCopyDownloadLink(document);
  });
})();
