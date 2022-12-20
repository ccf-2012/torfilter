// ==UserScript==
// @name         种子列表过滤
// @namespace    https://greasyfork.org/zh-CN/scripts/451748
// @version      0.9.9
// @license      GPL-3.0 License
// @description  在种子列表页中，过滤: 未作种，无国语，有中字，标题不含，描述不含，大小介于，IMDb/豆瓣大于输入值 的种子。配合dupapi可以实现Plex/Emby库查重。
// @author       ccf2012
// @source       https://github.com/ccf-2012/torfilter
// @icon         https://pterclub.com/favicon.ico
// @grant        GM_setClipboard
// @grant        GM.xmlHttpRequest
// @connect      localhost
// @require      https://code.jquery.com/jquery-3.6.0.min.js
// @match        https://pterclub.com/torrents.php*
// @match        https://pterclub.com/officialgroup*
// @match        https://pterclub.com/details.php*
// @match        https://chdbits.co/torrents.php*
// @match        https://chdbits.co/details.php*
// @match        https://audiences.me/torrents.php*
// @match        https://audiences.me/details.php*
// @match        https://ourbits.club/torrents.php*
// @match        https://ourbits.club/details.php*
// @match        https://springsunday.net/torrents.php*
// @match        https://springsunday.net/details.php*
// @match        https://www.beitai.pt/torrents.php*
// @match        https://www.beitai.pt/details.php*
// @match        https://totheglory.im/browse.php?*
// @match        https://totheglory.im/t/*
// @match        https://pt.keepfrds.com/torrents.php*
// @match        https://pt.keepfrds.com/details.php*
// @match        https://hdchina.org/torrents.php*
// @match        https://hdchina.org/details.php*
// @match        https://hdsky.me/torrents.php*
// @match        https://hdsky.me/details.php*

// ==/UserScript==

const not_supported = (element) => {
  return "";
};

const skip_passkey = async () => {
  return "";
};

//  ====== pter
const pter_imdbval = (element) => {
  var t = $(element).find(
    "td:nth-child(2) > table > tbody > tr > td > a:nth-child(1) > span"
  );
  return t.text();
};
const pter_imdbid = (element) => {
  var t = $(element).find("td:nth-child(2) > table > tbody > tr > td:nth-child(7) span");
  return (t && t.attr("data-imdbid")) ? 'tt'+t.attr("data-imdbid") : ''
};

const pter_douban = (element) => {
  var d = $(element).find(
    "td:nth-child(2) > table > tbody > tr > td > a:nth-child(2) > span"
  );
  return d.text();
};

const pter_seeding = (element) => {
  // var d = $(element).find("img.progbargreen");
  return ($(element).find("img.progbargreen").length > 0);
};

const pter_downed = (element) => {
  // var d = $(element).find("img.progbargreen");
  return ($(element).find("img.progbarred").length > 0);
};

//  ====== chd
const chd_imdb = (element) => {
  var t = $(element).find(
    "td:nth-child(2) > table > tbody > tr > td:nth-child(2)"
  );
  return t.text();
};

const chd_seeding = (element) => {
  var d = $(element).find("td:nth-child(10)");
  return (d.length > 0 && d.css("color") === 'rgb(0, 128, 0)')
  // return d.text() === "100%";
};

const chd_downed = (element) => {
  var d = $(element).find("td:nth-child(10)");
  // return (d.length > 0 && d.css("color") === 'rgb(0, 128, 0)')
  return d.text() != "--";
};


const chd_passkey = async () => {
  let html = await $.get("usercp.php");
  let passkeyRow = $(html).find('tr:contains("密钥"):last');
  if (passkeyRow.length > 0) {
    var key = passkeyRow.find("td:last").text();
    return "&passkey=" + key.trim();
  }
  return "";
};
//  ====== ade
const ade_imdbval = (element) => {
  var t = $(element).find(
    "td.rowfollow.torrents-box > div.torrents-name > table > tbody > tr > td:nth-child(2) > table > tbody > tr > td:nth-child(1) > div > a:nth-child(3)"
  );
  return t.text();
};
const ade_imdbid = (element) => {
  var t = $(element)
    .find(
      "td.rowfollow.torrents-box > div.torrents-name > table > tbody > tr > td:nth-child(2) > table > tbody > tr > td:nth-child(1) > div > a:nth-child(3)"
    )
    .attr("href");
  if (t) {
    var m = t.match(/title\/(tt\d+)/);
  }
  return m ? m[1] : "";
};

const ade_douban = (element) => {
  var d = $(element).find(
    "td.rowfollow.torrents-box > div.torrents-name > table > tbody > tr > td:nth-child(2) > table > tbody > tr > td:nth-child(1) > div > a:nth-child(1)"
  );
  return d.text();
};

const ade_seeding = (element) => {
  var d = $(element).find("div.torrents-progress");

  return d.length > 0 && d.css("width") != "0px";
  // return d.text() === "100%";
};

const ade_downed = (element) => {
  var d = $(element).find("div.torrents-progress2");

  return d.length > 0 && d.css("width") != "0px";
};


const ade_passkey = async () => {
    let html =  await $.get("usercp.php")
    // debugger;
    // $(html).find("#passkey").css("display", "");
    let passkeyRow = $(html).find("#passkey");
    if (passkeyRow.length > 0){
        let key = passkeyRow.text().replace('（妥善保管，请勿泄露）', '');
        return "&passkey=" + key.trim() + "&https=1" ;
    }
    return "" ;
};

//  ====== ob
const ob_imdbval = (element) => {
  var t = $(element).find(
    "td:nth-child(2) > table > tbody > tr > td:nth-child(4) > div:nth-child(1) > em > label"
  );
  return t.text();
};
const ob_imdbid = (element) => {
  var t = $(element)
    .find(
      "td:nth-child(2) > table > tbody > tr > td:nth-child(4) > div:nth-child(1) > em > label"
    )
    .attr("data-imdbid");

  return t ? "tt" + t : "";
};

const ob_douban = (element) => {
  var d = $(element).find(
    "td:nth-child(2) > table > tbody > tr > td:nth-child(4) > div:nth-child(2) > em > label"
  );
  return d.text();
};
const ob_seeding = (element) => {
  var d = $(element).find("div.doing");
  return d.length > 0 && d.attr("title").startsWith("100");
};
const ob_downed = (element) => {
  var d = $(element).find("div.out");
  return d.length > 0 && d.attr("title").startsWith("100");
};

const ob_passkey = async () => {
  let html = await $.get("usercp.php");

  let passkeyRow = $(html).find('tr:contains("密钥"):last');
  if (passkeyRow.length <= 0) {
    passkeyRow = $(html).find('tr:contains("密匙"):last');
  }
  if (passkeyRow.length <= 0) {
    passkeyRow = $(html).find('tr:contains("Passkey"):last');
  }
  if (passkeyRow.length > 0) {
    let key = passkeyRow.find("td:last").text();
    return "&passkey=" + key.trim() + "&https=1";
  }
  return "";
};

//  ====== ssd
const ssd_imdbval = (element) => {
  var t = $(element).find("span.torrent-rating");
  return $(t[0]).text()
  // let imdb = "";
  // if (t.parent().attr("href") && t.parent().attr("href").includes("imdb")) {
  //   imdb = t.text();
  // }
  // return imdb;
};

const ssd_imdbid = (element) => {
  var t = $(element)
    .find("td:nth-child(2) > div:nth-child(2) > span > a:nth-child(1)")
    .attr("href");
  if (t) {
    var m = t.match(/search=(\d+)\b.*search_area=4/);
    return m ? "tt" + m[1] : "";
  }
  return  "";
};

const ssd_douban = (element) => {
  var t = $(element).find("span.torrent-rating");
  return $(t[0]).text()
  // var d = $(element).find("td:nth-child(3) > div:nth-child(2) > a > span");
  // if (d.length <= 0) {
  //   d = $(element).find("td:nth-child(3) > div > a > span");
  // }
  // let douban = "";
  // if (d.parent().attr("href") && d.parent().attr("href").includes("douban")) {
  //   douban = d.text();
  // }
  // return douban;
};

const ssd_seeding = (element) => {
  var d = $(element).find("div.p_seeding");
  return d.length > 0;
};

const ssd_downed = (element) => {
  var d = $(element).find("div.p_inactive");
  return d.length > 0;
};

const ssd_passkey = async () => {
  // site changed 2022.12
  // let html = await $.get("usercp.php");
  // let passkeyRow = $(html).find('tr:contains("密钥"):last');
  // if (passkeyRow.length > 0) {
  //   var key = passkeyRow.find("td:last").text();
  //   return "&passkey=" + key.trim() + "&https=1";
  // }
  return "";
};

const ssd_detailTable = (html) => {
  let downTr = $(html).find('tr:contains("下载"):first');
  if (downTr) {
    return downTr.parent();
  } else return null;
};


//  ====== ttg
const ttg_imdbval = (element) => {
  var t = $(element).find("td:nth-child(2) > div.name_right > span.imdb_rate > a");
  return t.text();
};

const ttg_imdbid = (element) => {
  var t = $(element).find("td:nth-child(2) > div.name_right > span.imdb_rate > a").attr("href");
  if (t) {
    var m = t.match(/title\/(tt\d+)/);
  }
  return m ? m[1] : "";
};

const ttg_seeding = (element) => {
  var d = $(element).find("td:nth-child(2) > div.process.green > span");
  return d.length > 0;
};

const ttg_passkey = async () => {
  let html = await $.get("my.php");
  let passkeyRow = $("td", $(html)).filter(function() {
    return $(this).text() == "Passkey";
  }).closest("tr");

  if (passkeyRow.length > 0) {
    var key = passkeyRow.find("td:last").text();
    return key.trim();
  }
  return "";
};


// beitai
const beitai_seeding = (element) => {
  var d = $(element).find("td:nth-child(9)");
  return d.text().includes("100%");
};

const beitai_passkey = async () => {
  let html = await $.get("usercp.php");
  let passkeyRow = $(html).find('tr:contains("密钥"):last');
  if (passkeyRow.length > 0) {
    var key = passkeyRow.find("td:last").text();
    return "&passkey=" + key.trim() + "&https=1";
  }
  return "";
};

//  ====== frds
const frds_imdbval = (element) => {
  var t = $(element).find("td:nth-child(2) > table > tbody > tr > td:nth-child(2) > div:nth-child(1) > img:nth-child(2)");
  let imdb = "";
  if (t.attr("src") && t.attr("src").includes("imdb")) {
    imdb = t.parent().text();
    imdb = imdb.replace(/(-+|\d+\.\d*)\s*$/, '').trim()
  }
  return imdb;
};


const frds_passkey = async () => {
  let html = await $.get("usercp.php");
  let passkeyRow = $(html).find('tr:contains("密钥"):last');
  if (passkeyRow.length > 0) {
    var key = passkeyRow.find("td:last").text();
    return "&passkey=" + key.trim() + "&https=1";
  }
  return "";
};

const frds_seeding = (element) => {
  // var d = $(element).find("td:nth-child(2) > table > tbody > tr > td:nth-child(1) > div > div:nth-child(1)");
  var d = $("td:nth-child(2) > table > tbody > tr > td:nth-child(1)", element)
  return d.length > 0 && (/2s_up.gif/.exec(d.html()))
};

const frds_downed = (element) => {
  // var d = $(element).find("td:nth-child(2) > table > tbody > tr > td:nth-child(1) > div > div:nth-child(1)");
  var d = $("td:nth-child(2) > table > tbody > tr > td:nth-child(1)", element)
  return d.length > 0 && (/2s_dled.gif/.exec(d.html()))
};


//  ====== hdc
const hdc_imdbval = (element) => {
  var t = $(element).find(
    "td.t_name > table > tbody > tr > td.act > a.imdb"
  );
  return t.text();
};

const hdc_seeding = (element) => {
  var s = $(element).find("div.progress_seeding");
  var d = $(element).find("div.progressarea");
  return s.length > 0 || d.length > 0;
};
const hdc_downed = (element) => {
  var d = $(element).find("div.progress_completed");
  return d.length > 0;
};


//  ====== hds
const sky_imdbval = (element) => {
  var t = $(element).find(
    "td > table > tbody > tr > td:nth-child(2) > table > tbody > tr > td:nth-child(1) > div > a:nth-child(2)"
  );
  return t.text();
};
const sky_imdbid = (element) => {
  var t = $(element)
    .find(
      "td > table > tbody > tr > td:nth-child(2) > table > tbody > tr > td:nth-child(1) > div > a:nth-child(2)"
    )
    .attr("href");
  if (t) {
    var m = t.match(/title\/(tt\d+)/);
  }
  return m ? m[1] : "";

};

const sky_douban = (element) => {
  var d = $(element).find(
    "td > table > tbody > tr > td:nth-child(2) > table > tbody > tr > td:nth-child(1) > div > a:nth-child(1)"
  );
  return d.text();
};

const sky_seeding = (element) => {
  var s = $(element).find("div.progressseeding");
  var d = $(element).find("div.progressdownloading");
  return s.length > 0 || d.length > 0;
};

const sky_downed = (element) => {
  var d = $(element).find("div.progressfinished");

  return d && d.length > 0 ;
};

const sky_passkey = async () => {
  // let html = await $.get("usercp.php");
  // let passkeyRow = $(html).find('tr:contains("密钥"):last');
  // if (passkeyRow.length > 0) {
  //   var key = passkeyRow.find("td:last").text();
  //   return "&passkey=" + key.trim();
  // }
  return "";
};


var config = [
  {
    host: "pterclub.com",
    eleTorTable: "#torrenttable",
    eleCurPage: "#outer > table > tbody > tr > td > p:nth-child(4) > font",
    eleTorList: "#torrenttable > tbody > tr",
    eleTorItem: " table > tbody > tr > td > div > div:nth-child(1) > a",
    eleTorItemDesc: "table > tbody > tr > td > div > div:nth-child(2) > span",
    eleTorItemSize: "td:nth-child(5)",
    eleTorItemSeednum: "td:nth-child(6)",
    eleTorItemAdded: "td:nth-child(4) > span",
    useTitleName: 1,
    eleIntnTag: "a.chs_tag-gf",
    eleCnLangTag: "a.chs_tag-gy",
    eleCnSubTag: "a.chs_tag-sub",
    // eleCHNAreaTag: "img.chn",
    eleDownLink: "td:nth-child(2) > table > tbody > tr > td > a:first",
    eleCatImg: "td:nth-child(1) > a:nth-child(1) > img",
    eleDetailTitle: "#top",
    filterGY: true,
    filterZZ: true,
    funcIMDb: pter_imdbval,
    funcIMDbId: pter_imdbid,
    funcDouban: pter_douban,
    funcSeeding: pter_seeding,
    funcDownloaded: pter_downed,
    funcGetPasskey: skip_passkey,
  },
  {
    host: "chdbits.co",
    eleTorTable: "#outer > table > tbody > tr > td > table",
    eleCurPage: "#outer > table > tbody > tr > td > p:nth-child(3) > font",
    eleTorList: "#outer > table > tbody > tr > td > table > tbody > tr",
    eleTorItem: "td:nth-child(2) > table > tbody > tr > td:nth-child(1) > a",
    eleTorItemDesc:
      "td:nth-child(2) > table > tbody > tr > td:nth-child(1) > font",
    eleTorItemSize: "td:nth-child(5)",
    eleTorItemSeednum: "td:nth-child(6)",
    eleTorItemAdded: "td:nth-child(4) > span",
    useTitleName: 1,
    eleIntnTag: "div.tag-gf",
    eleCnLangTag: "div.tag-gy",
    eleCnSubTag: "div.tag-sub",
    eleDownLink:
      "td:nth-child(2) > table > tbody > tr > td:nth-child(2) > a:nth-child(1)",
    eleCatImg: "td:nth-child(1) > a:nth-child(1) > img",
    eleDetailTitle: "#top",
    filterGY: true,
    filterZZ: true,
    funcIMDb: chd_imdb,
    funcIMDbId: not_supported,
    funcDouban: not_supported,
    funcSeeding: chd_seeding,
    funcDownloaded: chd_downed,
    funcGetPasskey: chd_passkey,
  },
  {
    host: "audiences.me",
    eleTorTable: "#torrenttable",
    eleCurPage: "#outer > table > tbody > tr > td > p:nth-child(2) > font",
    eleTorList: "#torrenttable > tbody > tr",
    eleTorItem:
      "td.rowfollow.torrents-box > div.torrents-name > table > tbody > tr > td:nth-child(1) > a",
    eleTorItemDesc:
      "td > div.torrents-name > table > tbody > tr > td:nth-child(1) > span",
    eleTorItemSize: "td:nth-child(5)",
    eleTorItemSeednum: "td:nth-child(6)",
    eleTorItemAdded: "td:nth-child(4) > span",
    useTitleName: 1,
    eleIntnTag: "span.tgf",
    eleCnLangTag: "span.tgy",
    eleCnSubTag: "span.tzz",
    eleDownLink:
      "td > div.torrents-name > table > tbody > tr > td:nth-child(2) > table > tbody > tr > td:nth-child(2) > a:nth-child(1)",
    eleCatImg: "td:nth-child(1) > a > img",
    eleDetailTitle: "#top",
    filterGY: true,
    filterZZ: true,
    funcIMDb: ade_imdbval,
    funcIMDbId: ade_imdbid,
    funcDouban: ade_douban,
    funcSeeding: ade_seeding,
    funcDownloaded: ade_downed,
    funcGetPasskey: ade_passkey,
    // eleTorDetailTable: "tr:contains('副标题'):last",
  },
  {
    host: "ourbits.club",
    eleTorTable: "#torrenttable",
    eleCurPage: "#outer > table > tbody > tr > td > p:nth-child(7) > font",
    eleTorList: "#torrenttable > tbody > tr",
    eleTorItem: "td:nth-child(2) > table > tbody > tr > td:nth-child(1) > a",
    eleTorItemDesc: "td:nth-child(2) > table > tbody > tr > td:nth-child(1)",
    eleTorItemSize: "td:nth-child(5)",
    eleTorItemSeednum: "td:nth-child(6)",
    eleTorItemAdded: "td:nth-child(4) > span",
    useTitleName: 1,
    eleIntnTag: "div.tag-gf",
    eleCnLangTag: "div.tag-gy",
    eleCnSubTag: "div.tag-zz",
    eleDownLink:
      "td:nth-child(2) > table > tbody > tr > td:nth-child(5) > a:nth-child(1)",
    eleCatImg: "td:nth-child(1) > a:nth-child(1) > img",
    eleDetailTitle: "#top",
    filterGY: true,
    filterZZ: true,
    funcIMDb: ob_imdbval,
    funcIMDbId: ob_imdbid,
    funcDouban: ob_douban,
    funcSeeding: ob_seeding,
    funcDownloaded: ob_downed,
    funcGetPasskey: ob_passkey,
  },
  {
    host: "springsunday.net",
    eleTorTable: "table.torrents",
    eleCurPage: "#outer > table > tbody > tr > td > p:nth-child(3) > font",
    eleTorList: "table.torrents > tbody > tr",
    eleTorItem: "div.torrent-title > a",
    eleTorItemDesc: "div.torrent-smalldescr",
    eleTorItemSize: "td:nth-child(5)",
    eleTorItemSeednum: "td:nth-child(6)",
    eleTorItemAdded: "td:nth-child(4) > span",
    useTitleName: 1,
    eleIntnTag: "",
    eleCnLangTag: "",
    eleCnSubTag: "",
    eleDownLink:
      "table.torrentname > tbody > tr > td:nth-child(2)  a",
    eleCatImg: "td:nth-child(1) > a > img",
    eleDetailTitle: "#top",
    filterGY: false,
    filterZZ: false,
    funcIMDb: ssd_imdbval,
    funcIMDbId: ssd_imdbid,
    funcDouban: ssd_douban,
    funcSeeding: ssd_seeding,
    funcDownloaded: ssd_downed,
    funcGetPasskey: ssd_passkey,
  },
  {
    host: "totheglory.im",
    eleTorTable: "#torrent_table",
    eleCurPage: "#main_table > tbody > tr:nth-child(1) > td > p:nth-child(9) > a:nth-child(5) > b",
    eleTorList: "#torrent_table > tbody > tr",
    eleTorItem: "td:nth-child(2) > div.name_left > a > b",
    eleTorItemDesc: "td:nth-child(2) > div.name_left > a > b > span",
    eleTorItemSize: "td:nth-child(7)",
    eleTorItemSeednum: "td:nth-child(9) > b:nth-child(1)",
    eleTorItemAdded: "td:nth-child(5) > nobr",
    useTitleName: 3,
    eleIntnTag: "",
    eleCnLangTag: "",
    eleCnSubTag: "",
    eleDownLink:
      "td:nth-child(2) > div.name_right > span:nth-child(1) > a.dl_a",
    eleCatImg: "td:nth-child(1) > a > img",
    eleDetailTitle: "#top",
    filterGY: false,
    filterZZ: false,
    funcIMDb: ttg_imdbval,
    funcIMDbId: ttg_imdbid,
    funcDouban: not_supported,
    funcSeeding: ttg_seeding,
    funcDownloaded: not_supported,
    funcGetPasskey: ttg_passkey,
  },
  {
    host: "pt.keepfrds.com",
    eleTorTable: "#form_torrent > table",
    eleCurPage: "#outer > table > tbody > tr > td > p:nth-child(2) > font",
    eleTorList: "#form_torrent > table > tbody > tr",
    eleTorItem: "td:nth-child(2) > table > tbody > tr > td:nth-child(1) > a",
    eleTorItemDesc: "td:nth-child(2) > table > tbody > tr > td:nth-child(1)",
    eleTorItemSize: "td:nth-child(5)",
    eleTorItemSeednum: "td:nth-child(6) > b > a",
    eleTorItemAdded: "td:nth-child(4) > span",
    useTitleName: 2,
    eleIntnTag: "div.tag-gf",
    eleCnLangTag: "div.tag-gy",
    eleCnSubTag: "div.tag-zz",
    eleDownLink:
      "td:nth-child(2) > table > tbody > tr > td:nth-child(2) > div:nth-child(1) > a",
    eleCatImg: "td:nth-child(1) > a > img",
    eleDetailTitle: "#outer > table:nth-child(2) > tbody > tr:nth-child(2) > td.rowfollow",
    filterGY: false,
    filterZZ: false,
    funcIMDb: frds_imdbval,
    funcIMDbId: not_supported,
    funcDouban: not_supported,
    funcSeeding: frds_seeding,
    funcDownloaded: frds_downed,
    funcGetPasskey: frds_passkey,
  },
  {
    host: "www.beitai.pt",
    eleTorTable: "table.torrents",
    eleCurPage: "#outer > table > tbody > tr > td > p:nth-child(3) > font",
    eleTorList: "table.torrents > tbody > tr",
    eleTorItem: "td:nth-child(2) > table > tbody > tr > td:nth-child(1) > a",
    eleTorItemDesc: "td:nth-child(2) > table > tbody > tr > td:nth-child(1)",
    eleTorItemSize: "td:nth-child(5)",
    eleTorItemSeednum: "td:nth-child(6)",
    eleTorItemAdded: "td:nth-child(4) > span",
    useTitleName: 1,
    eleIntnTag: "div.tag-gf",
    eleCnLangTag: "div.tag-gy",
    eleCnSubTag: "div.tag-zz",
    eleDownLink:
      "td:nth-child(2) > table > tbody > tr > td:nth-child(2) > a:nth-child(1)",
    eleCatImg: "td:nth-child(1) > a > img",
    eleDetailTitle: "#top",
    filterGY: false,
    filterZZ: false,
    funcIMDb: not_supported,
    funcIMDbId: not_supported,
    funcDouban: not_supported,
    funcSeeding: beitai_seeding,
    funcDownloaded: not_supported,
    funcGetPasskey: beitai_passkey,
  }, 
  {
    host: "hdchina.org",
    eleTorTable: "#form_torrent > table",
    eleCurPage: "#site_content > div > div.pagenav_part > div > ul > li.active",
    eleTorList: "#form_torrent > table > tbody > tr",
    eleTorItem: "td.t_name > table > tbody > tr > td:nth-child(2) > h3 > a",
    eleTorItemDesc: "td.t_name > table > tbody > tr > td:nth-child(2) > h4",
    eleTorItemSize: "td.t_size",
    eleTorItemSeednum: "td.t_torrents > a",
    eleTorItemAdded: "td.t_time > span",
    useTitleName: 1,
    eleIntnTag: "div.tag-gf",
    eleCnLangTag: "div.tag-gy",
    eleCnSubTag: "div.tag-zz",
    eleDownLink: "td.t_name > table > tbody > tr > td:nth-child(2) > h3 > a",
    eleCatImg: "td.t_cat > a > img",
    eleDetailTitle: "#top",
    filterGY: false,
    filterZZ: false,
    funcIMDb: hdc_imdbval,
    funcIMDbId: not_supported,
    funcDouban: not_supported,
    funcSeeding: hdc_seeding,
    funcDownloaded: hdc_downed,
    funcGetPasskey: not_supported,
  },  
  {
    host: "hdsky.me",
    eleTorTable: "#outer > table > tbody > tr > td > table",
    eleCurPage: "#outer > table > tbody > tr > td > form:nth-child(8) > p > font",
    eleTorList: "#outer > table > tbody > tr > td > table > tbody > tr",
    eleTorItem: "td > table > tbody > tr > td:nth-child(1) > a",
    eleTorItemDesc: "td > table > tbody > tr > td:nth-child(1)",
    eleTorItemSize: "td:nth-child(5)",
    eleTorItemSeednum: "td:nth-child(6) > b > a",
    eleTorItemAdded: "td:nth-child(4) > span",
    useTitleName: 1,
    eleIntnTag: 'span:contains("官组")',
    eleCnLangTag: 'span:contains("国语")',
    eleCnSubTag: 'span:contains("中字")',
    eleDownLink:
      "td > table > tbody > tr > td:nth-child(1) > a",
    eleCatImg: "td.t_cat > a > img",
    eleDetailTitle: "#top",
    filterGY: true,
    filterZZ: true,
    funcIMDb: sky_imdbval,
    funcIMDbId: sky_imdbid,
    funcDouban: sky_douban,
    funcSeeding: sky_seeding,
    funcDownloaded: sky_downed,
    funcGetPasskey: sky_passkey,
  },  
];

var THISCONFIG = config.find((cc) => window.location.host.includes(cc.host));

function addFilterPanel() {
  var torTable = $(THISCONFIG.eleTorTable);
  if (torTable.length <= 0) {
    return;
  }

  var donwnloadPanel = `
  <table align='center'> <tr>
    <td style='width: 70px; border: none;'>
      <table>
        <tr>
          <td style='width: 65px; border: none;'>
            <input type="checkbox" id="chnsub" name="chnsub" value="uncheck"><label for="chnsub">有中字 </label>
          </td>
          </tr>
          <tr>
          <td style='width: 65px; border: none;'>
            <input type="checkbox" id="nochnlang" name="nochnlang" value="uncheck"><label for="nochnlang">无国语 </label>
          </td>
        </tr>
      </table>
    </td>
    <td style='width: 70px; border: none;'>
      <table>
        <tr>
          <td style='width: 65px; border: none;'>
          <input type="checkbox" id="seeding" name="seeding" value="uncheck"><label for="seeding">未作种 </label>
          </td>
        </tr>
        <tr>
          <td style='width: 65px; border: none;'>
            <input type="checkbox" id="downloaded" name="downloaded" value="uncheck"><label for="downloaded">未曾下 </label>
          </td>
        </tr>
      </table>
      </td>

      <td style='width: 200px; border: none;'>
        <table>
          <tr>
          <td style=' border: none;'>
          <div>标题不含 <input style='width: 130px;' id='titleregex' value="" />
          </div>
          </td>
        </tr><tr>
          <td style='border: none;'>
          <div>描述不含 <input style='width: 130px;' id='titledescregex' value="" />
          </div>
          </td>
        </tr>
      </table>
      </td>

      <td style='width: 120px; border: none;'>
      <div>大小介于 <input style='width: 50px;' id='sizerange' value="" />
      </div>
      </td>

      <td style='width: 120px; border: none;'>
      <div>IMDb/豆瓣 > <input style='width: 30px;' id='minimdb' value="0" />
      </div>
      </td>
      <td style='width: 60px; border: none;'>
          <button type="button" id="btn-filterlist" style="margin-top: 5px;margin-bottom: 5px;margin-left: 5px;">
          过滤
          </button>
      </td>
      <td style='width: 85px; border: none;'>
          <button type="button" id="btn-copydllink" style="margin-top: 5px;margin-bottom: 5px;margin-left: 5px;">
          拷贝链接
          </button>
      </td>
      <td style='width: 70px; border: none;'>
          <button type="button" id="btn-apicheckdupe" style="margin-top: 5px;margin-bottom: 5px;margin-left: 5px;">
          仅查重
          </button>
      </td>
      <td style='width: 70px; border: none;'>
          <button type="button" id="btn-apidownload" style="margin-top: 5px;margin-bottom: 5px;margin-left: 5px;">
          查&下
          </button>
      </td>
      <td style='width: 90px; border: none;'> <div id="process-log" style="margin-left: 5px;"></div> </td>
      </tr>
      </table>

  </body>
  </html>
`;
  torTable.before(donwnloadPanel);

  if (!THISCONFIG.filterGY) {
    $("#chnsub").parent().hide();
  }
  if (!THISCONFIG.filterZZ) {
    $("#nochnlang").parent().hide();
  }
}

function addDetailPagePanel() {
  $(`
  <div style=" width: 70px; height: 120px; position: fixed; top: 180px; right: 5px; z-index: 9999; ">
    <table align='center'> <tr>
    <td style='border: none;'>
        <button type="button" id="btn-detail-checkdupe" style="margin-top: 5px;margin-left: 5px;color: rgb(25, 118, 210);  justify-content: center; align-items: center;" >
        查重
        </button>
    </td>
    </tr>
    <tr>
    <td style=' border: none;'>
        <button type="button" id="btn-detail-forceapidownload" style="margin-top: 5px;margin-left: 5px;color: rgb(25, 118, 210);  justify-content: center; align-items: center;">
        下载
        </button>
    </td>
    </tr>
    <tr>
    <td style=' border: none;'>
        <button type="button" id="btn-detail-apidownload" style="margin-top: 5px;margin-left: 5px;color: rgb(25, 118, 210);  justify-content: center; align-items: center;">
        查&下
        </button>
    </td>
    </tr>
    <tr>
    <td style=' border: none;'> <div id="detail-log" style="margin-top: 10px;justify-content: center; align-items: center;"> </div> </td>
    </tr>
    </table>
  </div>
`
).appendTo("body");
}

function sizeStrToGB(sizeStr) {
  var regex = /[+-]?\d+(\.\d+)?/g;
  var sizeStr2 = sizeStr.replace(/,/g, "");
  var num = sizeStr2.match(regex).map(function (v) {
    return parseFloat(v);
  });
  var size = 0;
  if (sizeStr.match(/(KB|KiB)/i)) {
    size = num / 1024.0 / 1024.0;
  } else if (sizeStr.match(/(MB|MiB)/i)) {
    size = num / 1024.0;
  } else if (sizeStr.match(/(GB|GiB)/i)) {
    size = num;
  } else if (sizeStr.match(/(TB|TiB)/i)) {
    size = num * 1024.0;
  } else {
    size = num / 1024.0 / 1024.0 / 1024.0;
  }

  return size;
}

function getTorSizeRange(rangestr) {
  let m = rangestr.match(/(\d+)([,，-]\s*(\d+))?/);
  if (m) {
    return [parseInt(m[1]) || 0, parseInt(m[3]) || 0];
  }
  return [0, 0];
}

function saveToCookie(filterParam) {
  var cookie_name = "filterParam";
  var cookie_value = filterParam;
  var d = new Date();
  // change expire time here, 60 * 1000 for 1 minute
  // d.setTime(d.getTime() + ( 60 * 1000));
  // this is 3 days
  d.setTime(d.getTime() + 300 * 24 * 60 * 60 * 1000);
  var expires = "expires=" + d.toUTCString();
  document.cookie =
    cookie_name + "=" + cookie_value + ";" + expires + ";path=/";
}

function saveParamToCookie() {
  let paramStr =
    "minimdb=" +
    $("#minimdb").val() +
    "&sizerange=" +
    $("#sizerange").val() +
    "&titleregex=" +
    $("#titleregex").val() +
    "&descregex=" +
    $("#titledescregex").val() +
    "&seeding=" +
    $("#seeding").is(":checked") +
    "&downloaded=" +
    $("#downloaded").is(":checked") +
    "&chnsub=" +
    $("#chnsub").is(":checked") +
    "&nochnlang=" +
    $("#nochnlang").is(":checked");
  saveToCookie(paramStr);
}

const getCookieValue = (name) =>
  document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)")?.pop() || "";

function loadParamFromCookie() {
  var cc = getCookieValue("filterParam");
  if (cc) {
    fillParam(cc);
  }
}

function fillParam(filterParam) {
  var paraList = filterParam.split("&");
  for (var i = 0; i < paraList.length; i++) {
    var m = paraList[i].match(/(\w+)\=(.*)/);
    if (m) {
      if (m[1] == "minimdb") {
        $("#minimdb").val(m[2]);
      }
      if (m[1] == "sizerange") {
        $("#sizerange").val(m[2]);
      }
      if (m[1] == "titleregex") {
        $("#titleregex").val(m[2]);
      }
      if (m[1] == "descregex") {
        $("#titledescregex").val(m[2]);
      }
      if (m[1] == "seeding") {
        $("#seeding").prop("checked", m[2] == "true");
      }
      if (m[1] == "downloaded") {
        $("#downloaded").prop("checked", m[2] == "true");
      }
      if (m[1] == "chnsub") {
        $("#chnsub").prop("checked", m[2] == "true");
      }
      if (m[1] == "nochnlang") {
        $("#nochnlang").prop("checked", m[2] == "true");
      }
    }
  }
}

function getItemTitle(item) {
  let titlestr = "";

  if (THISCONFIG.useTitleName == 1) {
    titlestr = item.attr("title");
  } else if (THISCONFIG.useTitleName == 0) {
    titlestr = item.text();
  } else if (THISCONFIG.useTitleName == 2) {
    var elebr = item.parent().children("br").get(0);
    if (elebr) {
      var eletitle = elebr.nextSibling;
      if (eletitle.data) titlestr = eletitle.data;
      else if (eletitle.firstChild.data) titlestr = eletitle.firstChild.data;
    }
  } else if (THISCONFIG.useTitleName == 3) {
    let titlehtml = item.html()
    titlestr = titlehtml.substring(0, titlehtml.indexOf('<br><span'));
  }
  else if (THISCONFIG.useTitleName == 4) {
    let ele2 = item.parent().find("[href*='details']")
    titlestr = ele2.attr("title");
  }
  return titlestr.trim();
}

var onClickFilterList = (html) => {
  $("#process-log").text("处理中...");
  let torlist = $(html).find(THISCONFIG.eleTorList);
  let imdbMinVal = parseFloat($("#minimdb").val()) || 0.0;
  let sizerange = getTorSizeRange($("#sizerange").val());
  saveParamToCookie();
  let filterCount = 0;
  for (let index = 1; index < torlist.length; ++index) {
    let element = torlist[index];
    let item = $(element).find(THISCONFIG.eleTorItem);
    if (item.length <= 0) {
      continue;
    }

    let titlestr = getItemTitle(item);
    let keepShow = true;

    if (sizerange[0] || sizerange[1]) {
      let sizestr = $(element).find(THISCONFIG.eleTorItemSize).text().trim();
      let torsize = 0;
      if (sizestr) {
        torsize = sizeStrToGB(sizestr);
      }
      if (sizerange[0] && torsize < sizerange[0]) {
        keepShow = false;
      }
      if (sizerange[1] && torsize > sizerange[1]) {
        keepShow = false;
      }
    }

    var seednum = $(element).find(THISCONFIG.eleTorItemSeednum).text().trim();
    seednum = seednum.replace(/\,/g, "");
    if (!seednum) {
      seednum = " ";
    }

    var tortime;
    if ($(element).find(THISCONFIG.eleTorItemAdded)[0]) {
      tortime = $(element).find(THISCONFIG.eleTorItemAdded)[0].title;
    }
    if (!tortime) {
      tortime = " ";
    }

    let imdbval = parseFloat(THISCONFIG.funcIMDb(element)) || 0.0;
    let doubanval = parseFloat(THISCONFIG.funcDouban(element)) || 0.0;
    if (imdbMinVal > 0.1 && imdbval < imdbMinVal && doubanval < imdbMinVal) {
      keepShow = false;
    }
    if ($("#titleregex").val()) {
      let regex = new RegExp($("#titleregex").val(), "gi");
      if (titlestr.match(regex)) {
        keepShow = false;
      }
    }
    let titledesc = ""
    if ($("#titledescregex").val()) {
      let regex = new RegExp($("#titledescregex").val(), "gi");
      let titleele = $(element).find(THISCONFIG.eleTorItemDesc);
      if (titleele){
        titledesc = titleele.text()
        titledesc = titledesc.replace(/[\n\r]+/g, '');
        titledesc = titledesc.replace(/\s{2,10}/g, ' ');
      }
      if (titledesc.match(regex)) {
        keepShow = false;
      }
    }

    // if ($("#intn_tor").is(":checked") && $(torlist[index]).find(THISCONFIG.eleIntnTag).length <= 0) {
    //     keepShow = false;
    // }
    if ($("#seeding").is(":checked") && THISCONFIG.funcSeeding(element)) {
      keepShow = false;
    }
    if ($("#downloaded").is(":checked") && THISCONFIG.funcDownloaded(element)) {
      keepShow = false;
    }
    if (
      THISCONFIG.filterZZ &&
      $("#chnsub").is(":checked") &&
      $(torlist[index]).find(THISCONFIG.eleCnSubTag).length <= 0
    ) {
      keepShow = false;
    }
    if (
      THISCONFIG.filterGY &&
      $("#nochnlang").is(":checked") &&
      $(torlist[index]).find(THISCONFIG.eleCnLangTag).length > 0
    ) {
      keepShow = false;
    }

    if (keepShow) {
      $(element).show();
    } else {
      $(element).hide();
      console.log("Filtered: "+ titlestr+" : "+titledesc)
      filterCount++;
    }
  }
  $("#process-log").text("过滤了：" + filterCount);
};

var asyncCopyLink = async (html) => {
  $("#process-log").text("处理中...");
  let passKeyStr = await THISCONFIG.funcGetPasskey();
  // console.log(passKeyStr);

  let torlist = $(html).find(THISCONFIG.eleTorList);
  var resulttext = "";
  for (let index = 1; index < torlist.length; ++index) {
    if ($(torlist[index]).is(":visible")) {
      let dllink = getDownloadLink(torlist[index], passKeyStr);
      if (dllink) {
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

var SUM_SIZE;

var postToFilterDownloadApi = async (tordata, doDownload, ele) => {
  var apiUrl = doDownload ? "http://localhost:3006/p/api/v1.0/dupedownload" : "http://localhost:3006/p/api/v1.0/checkdupeonly"
  let sizestr = $(ele).find(THISCONFIG.eleTorItemSize).text().trim();
  let torsize = 0;
  if (sizestr) {
    torsize = sizeStrToGB(sizestr);
  }
  var resp = GM.xmlHttpRequest({
    method: "POST",
    url: apiUrl,
    data: JSON.stringify(tordata),
    headers: {
      "Content-Type": "application/json",
    },
    onload: function (response) {
      if (response.status == 202) {
        $(ele).css("background-color", "lightgray");
        // console.log("Dupe: " + tordata.torname);
      } else if (response.status == 201) {
        let p = doDownload ? "下载 " : "无重 "
        SUM_SIZE += (parseInt(torsize) || 0);
        $("#process-log").text(p + SUM_SIZE+" GB");
        if (doDownload){
          $(ele).css("background-color", "darkseagreen");
        }
        else {
          $(ele).css("background-color", "LightBlue"); // CadetBlue, CornflowerBlue DodgerBlue DarkTurquoise
        }
        // console.log("Add download: " + tordata.torname);
      } else if (response.status == 205) {
        $(ele).css("background-color", "darkturquoise");
        // console.log("no dupe but no download: " + tordata.torname);
      } else if (response.status == 203) {
        $(ele).css("background-color", "lightpink");
        // console.log("TMDbNotFound: " + tordata.torname);
      } else {
        $(ele).css("background-color", "red");
        console.log(response);
      }
    },
    onerror: function (reponse) {
      //alert('error');
      console.log("error: ", reponse);
    },
  });
};

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function _getDownloadUrlByPossibleHrefs(pagehtml) {
  const possibleHrefs = [
    // misc
    "a[href*='passkey']",
    // pthome, ade
    "a[href*='downhash'][href*='https']",
    "a[href*='passkey'][href*='https']",
    // hdchina
    "a[href*='hash'][href*='https']",
    "a[href*='https://totheglory.im/dl/']"
  ];

  if (window.location.host == "pt.keepfrds.com"){
    //frds
    const dllink = $("input[value*='passkey']", pagehtml);
    if (dllink.length){
      return dllink.prop("value")
    }
  }
  for (const href of possibleHrefs) {
    const query = $(href, pagehtml);
    if (query.length) {
      return query.prop("href");
    }
  }
  return null;
}


function getHDCuid() {
  let bodytext = $("body").html();
  let datas = /userdetails\.php\?id=(\d+)/.exec( bodytext );
  if (datas && datas.length > 1) {
    return datas[1];
  }
  return "";
}


function getIMDb() {
  let bodytext = $("body").html();
  let datas = /www\.imdb\.com\/title\/(tt\d+)/.exec( bodytext );
  if (datas && datas.length > 1) {
    return datas[1];
  }
  return "";
}

var postToDetailCheckDupeApi = async (apiurl, tordata) => {
  let logele = "#detail-log";
  let down = apiurl.indexOf('download')>0 ? true : false
  var resp = GM.xmlHttpRequest({
    method: "POST",
    url: apiurl,
    data: JSON.stringify(tordata),
    headers: {
      "Content-Type": "application/json",
    },
    onload: function (response) {
      if (response.status == 202) {
        $(logele).parent().parent().css("background-color", "lightgray");
        $(logele).text("重复.");
      } else if (response.status == 201) {
        $(logele).parent().parent().css("background-color", "darkseagreen");
        $(logele).text(down? "添加下载": "无重复.");
      } else if (response.status == 205) {
        $(logele).parent().parent().css("background-color", "darkturquoise");
        $(logele).text("无下载链接.");
      } else if (response.status == 203) {
        $(logele).parent().parent().css("background-color", "lightpink");
        $(logele).text("TMDbNotFound.");
      } else {
        $(logele).parent().parent().css("background-color", "red");
        $(logele).text("出错.");
      }
    },
    onerror: function (reponse) {
      //alert('error');
      console.log("error: ", reponse);
    },
  });
};

var asyncDetailApiDownload = async (html, forcedl) => {
  $("#detail-log").text("处理中...");
  // dllink = $("#torrent_dl_url > a").href()
  // TODO:
  let titlestr = getDetailTitle();

  let dllink = _getDownloadUrlByPossibleHrefs(html);
  if (dllink) {
    let imdbid = getIMDb();
    var tordata = {
      torname: titlestr,
      imdbid: imdbid,
      downloadlink: dllink,
      force: forcedl
    };
    await postToDetailCheckDupeApi(
      "http://localhost:3006/p/api/v1.0/dupedownload",
      tordata
    );
  }
};


var getDetailPageIMDbAndDlink = async (downloadLink) => {
  let m = downloadLink.match(/\?id=(\d+)/);
  if (!m) {
    return ["", downloadLink];
  }
  var torrentId = m[1];

  let detailhtml = await $.get("/details.php?id="+torrentId);
  let datas = /www\.imdb\.com\/title\/(tt\d+)/.exec( detailhtml );
  let dllink = _getDownloadUrlByPossibleHrefs(detailhtml);
  if (!dllink) {
    dllink = downloadLink;
  }
  if (datas && datas.length > 1) {
    return [datas[1], dllink];
  }
  else {
    return ["", dllink];
  }
}


function linkPasskey(link, passKeyStr) {
  if (THISCONFIG.host == "totheglory.im")
  {
    return link.replace(/\d+$/, "") + passKeyStr;
  }
  else{
    return link + passKeyStr;
  }
}


function getDownloadLink(element, passKeyStr){
  let hrefele = $(element).find(THISCONFIG.eleDownLink);
  if (hrefele.length > 0) {
    let url = hrefele.prop("href");
    let dllink = "";
    if (THISCONFIG.host == "hdchina.org"){
      let uidstr = getHDCuid();
      dllink = linkPasskey(url, passKeyStr) + "&uid=" + uidstr;
    }
    else {
      dllink = linkPasskey(url, passKeyStr);
    }
    // let dllink = linkPasskey(url, passKeyStr);
 
    return dllink
  }
  return ""
}

var DUPECHECKED = false;
var asyncApiDownload = async (html, doDownload) => {
  let dupeChecked = DUPECHECKED 
  $("#process-log").text("处理中...");
  let passKeyStr = await THISCONFIG.funcGetPasskey();
  SUM_SIZE = 0;
  let torlist = $(html).find(THISCONFIG.eleTorList);
  for (let index = 1; index < torlist.length; ++index) {
    if ($(torlist[index]).is(":visible")) {
      let element = torlist[index];
      let item = $(element).find(THISCONFIG.eleTorItem);

      let seednum = parseInt($(element).find(THISCONFIG.eleTorItemSeednum).text().trim()) || 0;
      
      if (item.length == 0) { continue}
      // refer to Line 978:
      // } else if (response.status == 201) {
      //   $(ele).css("background-color", "darkseagreen"); 'rgb(143, 188, 143)'
       if (doDownload && dupeChecked && $(element).css('background-color') != 'rgb(173, 216, 230)') {
        continue;
      }

      let titlestr = getItemTitle(item);
      let imdbid = THISCONFIG.funcIMDbId(element);
      let dllink = getDownloadLink(torlist[index], passKeyStr);

      if (dllink && seednum > 0) {
        // check detal page imdb only when doDownload
        // hdsky exception: need fetch detail page
        if (doDownload && (!imdbid  || THISCONFIG.host == "hdsky.me")) {
          let res = await getDetailPageIMDbAndDlink(dllink);
          imdbid = res[0];
          dllink = res[1];
          console.log(titlestr, imdbid);
        }
        var tordata = {
          torname: titlestr,
          imdbid: imdbid,
          downloadlink: dllink,
        };
        await postToFilterDownloadApi(tordata, doDownload, element);
        if (doDownload){
          await sleep(2000);
        }
        else {
          await sleep(200);
        }
      }
    }
  }
  if (doDownload){
    $("#process-log").text("查重下载已提交");
  }
  else {
    $("#process-log").text("查重已提交");
    DUPECHECKED = true;
  }
};

function onClickApiDownload(html) {
  asyncApiDownload(html, true);
}

function onClickApiCheckDupe(html) {
  asyncApiDownload(html, false);
}

function onClickDetailDownload(html) {
  asyncDetailApiDownload(html, false);
}

function onClickDetailForceDownload(html) {
  asyncDetailApiDownload(html, true);
}

function getDetailTitle() {
  let titlestr = $(THISCONFIG.eleDetailTitle).text().trim();
  titlestr = titlestr.replace(/\[?禁转\s*/, "")
  titlestr = titlestr.replace(/\[[^\]]+\]\s*$/, "")
  titlestr = titlestr.replace(/\s*\[(50%|30%|(2X)?免费)\].*$/, "")
  titlestr = titlestr.replace(/\s*\(限时.*$/, "").trim()
  return titlestr;
}

var asyncDetailCheckDupe = async (html) => {
  $("#detail-log").text("处理中..");
  // dllink = $("#torrent_dl_url > a").href()
  // let titlestr = $("#top").text();
  let titlestr = getDetailTitle();
  let dllink = _getDownloadUrlByPossibleHrefs(html);
  if (dllink) {
    let imdbid = getIMDb();
    var tordata = {
      torname: titlestr,
      imdbid: imdbid,
      downloadlink: dllink,
    };
    await postToDetailCheckDupeApi(
      "http://localhost:3006/p/api/v1.0/checkdupeonly",
      tordata
    );
  }
  else {
    console.log("download link not found.")
    $("#detail-log").text("无下载链接");
  }
};

function onClickDetailCheckDup(html) {
  asyncDetailCheckDupe(html);
}


function addAdoptColumn(html) {
  // const torTable = $(THISCONFIG.eleTorTable);
  if (THISCONFIG.host != "pterclub.com") {
    return;
  }
  const idregex = /id=(\d+)/;

  var torlist = $(html).find(THISCONFIG.eleTorList);
  for (let index = 0; index < torlist.length; ++index) {
    let element = torlist[index];
    let item = $(element).find(THISCONFIG.eleTorItem);
    let href = item.attr("href");
    if (href) {
      let torid = href.match(idregex);
      if (torid) {
        let sizeele = $(element).find(THISCONFIG.eleTorItemSize);
        $(element).append(
          "<td ><a href=/viewclaims.php?add_torrent_id=" +
            torid[1] +
            "> 认领</a></td>"
        );
      }
    } else {
      $(element).append('<td class="colhead"> 认领种子 </td>');
    }
  }
}

(function () {
  "use strict";
  if (THISCONFIG) {
    if (window.location.href.match(/details.php/) ||
        window.location.href.match(/totheglory.im\/t/) ) {
      addDetailPagePanel();
      $("#btn-detail-checkdupe").click(function () {
        onClickDetailCheckDup(document);
      });
      $("#btn-detail-apidownload").click(function () {
        onClickDetailDownload(document);
      });
      $("#btn-detail-forceapidownload").click(function () {
        onClickDetailForceDownload(document);
      });
    } else {
      addAdoptColumn(document);
      addFilterPanel();
      loadParamFromCookie();
      $("#btn-filterlist").click(function () {
        onClickFilterList(document);
      });
      $("#btn-copydllink").click(function () {
        onClickCopyDownloadLink(document);
      });
      $("#btn-apidownload").click(function () {
        onClickApiDownload(document);
      });
      $("#btn-apicheckdupe").click(function () {
        onClickApiCheckDupe(document);
      });
    }
  }
})();
