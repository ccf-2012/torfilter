// ==UserScript==
// @name         种子列表过滤与认领
// @namespace    https://greasyfork.org/zh-CN/scripts/451748
// @version      0.4
// @license      GPL-3.0 License
// @description  在种子列表页中，过滤: 未作种， 无国语，有中字，标题不含，描述不含，以及imdb大于输入值 的种子
// @author       ccf2012
// @icon         https://pterclub.com/favicon.ico
// @grant        GM_setClipboard
// @grant        GM_xmlhttpRequest
// @require      https://code.jquery.com/jquery-3.6.0.min.js
// @match        https://pterclub.com/torrents.php*
// @match        https://pterclub.com/officialgroup*
// @match        https://chdbits.co/torrents.php*
// @match        https://audiences.me/torrents.php*
// @match        https://ourbits.club/torrents.php*
// @match        https://springsunday.net/torrents.php*

// ==/UserScript==


const not_supported  = (element) => {
    return  ''
  };
  
const pter_imdb = (element) => {
    var t = $(element).find("td:nth-child(2) > table > tbody > tr > td > a:nth-child(1) > span");
    return t.text();
};
const pter_douban = (element) => {
    var d = $(element).find("td:nth-child(2) > table > tbody > tr > td > a:nth-child(2) > span");
    return d.text();
};

const pter_seeding = (element) => {
    var d = $(element).find("img.progbargreen");
    return (d.length > 0);
};

const chd_imdb = (element) => {
    var t = $(element).find("td:nth-child(2) > table > tbody > tr > td:nth-child(2)");
    return t.text();
};

const chd_seeding = (element) => {
    var d = $(element).find("td:nth-child(10)");
    return (d.length > 0 && d.css("color") === 'rgb(0, 128, 0)')
    // return (d.text() === "100%")
};

const ade_imdb = (element) => {
    var t = $(element).find("td.rowfollow.torrents-box > div.torrents-name > table > tbody > tr > td:nth-child(2) > table > tbody > tr > td:nth-child(1) > div > a:nth-child(3)");
    return t.text();
};
const ade_douban = (element) => {
    var d = $(element).find("td.rowfollow.torrents-box > div.torrents-name > table > tbody > tr > td:nth-child(2) > table > tbody > tr > td:nth-child(1) > div > a:nth-child(1)");
    return d.text();
};
const ade_seeding = (element) => {
    var d = $(element).find("div.torrents-progress");
    return (d.length > 0 && d.css("width") != '0px')
    // return d.text() === "100%";
};

const ob_imdb = (element) => {
    var t = $(element).find("td:nth-child(2) > table > tbody > tr > td:nth-child(4) > div:nth-child(1) > em > label");
    return t.text();
};
const ob_douban = (element) => {
    var d = $(element).find("td:nth-child(2) > table > tbody > tr > td:nth-child(4) > div:nth-child(2) > em > label");
    return d.text();
};
const ob_seeding = (element) => {
    var d = $(element).find("div.progressBar");
    return ((d.length > 0) && (d.attr("title").startsWith('100')))
};


const ssd_imdb = (element) => {
    var t = $(element).find("td:nth-child(3) > div:nth-child(1) > a > span");
    let imdb = "";
    if (t.parent().attr("href") && t.parent().attr("href").includes("imdb")){
        imdb = t.text()
    }
    return imdb;
};
const ssd_douban = (element) => {
    var d = $(element).find("td:nth-child(3) > div:nth-child(2) > a > span");
    if (!d){
        d = $(element).find("td:nth-child(3) > div > a > span");
    }
    let douban = "";
    if (t.parent().attr("href") && t.parent().attr("href").includes("douban")){
        douban = t.text()
    }
    return douban;
};
const ssd_seeding = (element) => {
    var d = $(element).find("div.p_seeding");
    return (d.length > 0);
};


var config = [
    {
        host: "pterclub.com",
        eleTorTable: "#torrenttable",
        eleCurPage: "#outer > table > tbody > tr > td > p:nth-child(4) > font",
        eleTorList: "#torrenttable > tbody > tr",
        eleTorItem:
            " table > tbody > tr > td > div > div:nth-child(1) > a",
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
        filterGY: true,
        filterZZ: true,
        funcIMDb:pter_imdb,
        funcDouban:pter_douban,
        funcSeeding: pter_seeding,    
    },
    {
        host: "chdbits.co",
        eleTorTable: "#outer > table > tbody > tr > td > table",
        eleCurPage: "#outer > table > tbody > tr > td > p:nth-child(3) > font",
        eleTorList: "#outer > table > tbody > tr > td > table > tbody > tr",
        eleTorItem: "td:nth-child(2) > table > tbody > tr > td:nth-child(1) > a",
        eleTorItemDesc: "td:nth-child(2) > table > tbody > tr > td:nth-child(1) > font",
        eleTorItemSize: "td:nth-child(5)",
        eleTorItemSeednum: "td:nth-child(6)",
        eleTorItemAdded: "td:nth-child(4) > span",
        useTitleName: 1,
        eleIntnTag: "div.tag-gf",
        eleCnLangTag: "div.tag-gy",
        eleCnSubTag: "div.tag-sub",
        eleDownLink: "td:nth-child(2) > table > tbody > tr > td:nth-child(2) > a:nth-child(1)",
        eleCatImg: "td:nth-child(1) > a:nth-child(1) > img",
        filterGY: true,
        filterZZ: true,
        funcIMDb:chd_imdb,
        funcDouban:not_supported,
        funcSeeding: chd_seeding,    
      },
      {
        host: "audiences.me",
        eleTorTable: "#torrenttable",
        eleCurPage: "#outer > table > tbody > tr > td > p:nth-child(2) > font",
        eleTorList: "#torrenttable > tbody > tr",
        eleTorItem:
          "td.rowfollow.torrents-box > div.torrents-name > table > tbody > tr > td:nth-child(1) > a",
        eleTorItemDesc: "td > div.torrents-name > table > tbody > tr > td:nth-child(1) > span",
        eleTorItemSize: "td:nth-child(5)",
        eleTorItemSeednum: "td:nth-child(6)",
        eleTorItemAdded: "td:nth-child(4) > span",
        useTitleName: 1,
        eleIntnTag: "span.tgf",
        eleCnLangTag: "span.tgy",
        eleCnSubTag: "span.tzz",
        eleDownLink: "td > div.torrents-name > table > tbody > tr > td:nth-child(2) > table > tbody > tr > td:nth-child(2) > a:nth-child(1)",
        eleCatImg: "td:nth-child(1) > a > img",
        filterGY: true,
        filterZZ: true,
        funcIMDb:ade_imdb,
        funcDouban:ade_douban,
        funcSeeding: ade_seeding,    
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
        eleDownLink: "td:nth-child(2) > table > tbody > tr > td:nth-child(5) > a:nth-child(1)",
        eleCatImg: "td:nth-child(1) > a:nth-child(1) > img",
        filterGY: true,
        filterZZ: true,
        funcIMDb:ob_imdb,
        funcDouban:ob_douban,
        funcSeeding: ob_seeding,    
      },
      {
        host: "springsunday.net",
        eleTorTable: "table.torrents",
        eleCurPage: "#outer > table > tbody > tr > td > p:nth-child(3) > font",
        eleTorList: "table.torrents > tbody > tr",
        eleTorItem: "td:nth-child(2) > table > tbody > tr > td:nth-child(1) > a",
        eleTorItemDesc: "td:nth-child(2) > table > tbody > tr > td:nth-child(1)",
        eleTorItemSize: "td:nth-child(6)",
        eleTorItemSeednum: "td:nth-child(7)",
        eleTorItemAdded: "td:nth-child(5) > span",
        useTitleName: 1,
        eleIntnTag: "",
        eleCnLangTag: "",
        eleCnSubTag: "",
        eleDownLink: "td:nth-child(2) > table > tbody > tr > td:nth-child(2) > a:nth-child(1)",
        eleCatImg: "td:nth-child(1) > a > img",
        filterGY: false,
        filterZZ: false,
        funcIMDb:ssd_imdb,
        funcDouban:ssd_douban,
        funcSeeding: ssd_seeding,    
      },      
]


var THISCONFIG = config.find((cc) => window.location.host.includes(cc.host));

function addFilterPanel() {
    var torTable = $(THISCONFIG.eleTorTable);

    var donwnloadPanel = `
    <table align='center'> <tr>
    <td style='width: 70px; border: none;'>
    <input type="checkbox" id="seeding" name="seeding" value="uncheck"><label for="seeding">未作种 </label>
    </td>
    `
    if (THISCONFIG.filterGY){
        donwnloadPanel +=     `
        <td style='width: 70px; border: none;'>
        <input type="checkbox" id="chnsub" name="chnsub" value="uncheck"><label for="chnsub">有中字 </label>
        </td>
`    
    }
    if (THISCONFIG.filterZZ){
        donwnloadPanel +=     `
    <td style='width: 70px; border: none;'>
    <input type="checkbox" id="nochnlang" name="nochnlang" value="uncheck"><label for="nochnlang">无国语 </label>
    </td>
    `
    }
    donwnloadPanel +=
    `
    <td style='width: 180px; border: none;'>
    <div>标题不含 <input style='width: 100px;' id='titleregex' value="" />
    </div>
    </td>    
    <td style='width: 180px; border: none;'>
    <div>描述不含 <input style='width: 110px;' id='titledescregex' value="" />
    </div>
    </td>    
    <td style='width: 90px; border: none;'>
    <div>IMDb > <input style='width: 30px;' id='minimdb' value="0" />
    </div>
    </td>    
    <td style='width: 70px; border: none;'>
        <button type="button" id="btn-filterlist" style="margin-top: 5px;margin-bottom: 5px;margin-left: 5px;padding: 5px 10px;">
        过滤
        </button>
        </td>
    <td style='width: 100px; border: none;'>
        <button type="button" id="btn-downloadfiltered" style="margin-top: 5px;margin-bottom: 5px;margin-left: 5px;padding: 5px 10px;">
        拷贝链接
        </button>

    </td>
    <td style='width: 120px; border: none;'> <div id="process-log" style="margin-left: 5px;padding: 5px 10px;"></div> </td>
    </tr>
    </table>
`
    torTable.before(donwnloadPanel);
}

var onClickFilterList = (html) => {
    $("#process-log").text("处理中...");
    let torlist = $(html).find(THISCONFIG.eleTorList);

    let filterCount = 0;
    for (let index = 1; index < torlist.length; ++index) {
        let element = torlist[index];
        let item = $(element).find(THISCONFIG.eleTorItem);
        let titlestr = '';

        if (item.length <= 0 ) {
            continue;
        }
        if (THISCONFIG.useTitleName === 1) {
            titlestr = item.attr("title");
        } else if (THISCONFIG.useTitleName === 0) {
            titlestr = item.text();
        } else if (THISCONFIG.useTitleName === 2) {
            var elebr = item.parent().children('br').get(0)
            if (elebr){
              var eletitle = elebr.nextSibling; 
              if (eletitle.data) titlestr = eletitle.data
              else if (eletitle.firstChild.data) titlestr = eletitle.firstChild.data
            }
        }     

        let imdbval = parseFloat(THISCONFIG.funcIMDb(element))  || 0.0;
        let imdbminval = parseFloat($("#minimdb").val()) || 0.0;
        let keepShow = true;
        if ( imdbminval > 0.1 && imdbval < imdbminval){
            keepShow = false;
        }
        if ($("#titleregex").val()){
            let regex = new RegExp( $("#titleregex").val(), 'gi');
            if (titlestr.match(regex)) {
                keepShow = false;
            }
        }
        if ($("#titledescregex").val()){
            let regex = new RegExp( $("#titledescregex").val(), 'gi');
            titledesc = $(element).find(THISCONFIG.eleTorItemDesc);
            if (titledesc.text().match(regex)) {
                keepShow = false;
            }
        }

        // if ($("#intn_tor").is(":checked") && $(torlist[index]).find(THISCONFIG.eleIntnTag).length <= 0) {
        //     keepShow = false;
        // }
        if ($("#seeding").is(":checked") && THISCONFIG.funcSeeding(element)) {
            keepShow = false;
        }
        if (THISCONFIG.filterZZ && $("#chnsub").is(":checked") && $(torlist[index]).find(THISCONFIG.eleCnSubTag).length <= 0) {
            keepShow = false;
        }
        if (THISCONFIG.filterGY && $("#nochnlang").is(":checked") && $(torlist[index]).find(THISCONFIG.eleCnLangTag).length > 0) {
            keepShow = false;
        }

        if (keepShow){
            $(element).show();
        }
        else {
            $(element).hide();
            filterCount ++;
        }
    }
    $("#process-log").text("过滤了：" + filterCount );
};

function onClickDownloadFiltered(html) {
    $("#process-log").text('处理中...')
    let torlist = $(html).find(THISCONFIG.eleTorList);
    var resulttext = '';
    for (let index = 1; index < torlist.length; ++index) {
        if ($(torlist[index]).is(":visible")) {
            let hrefele = $(torlist[index]).find(THISCONFIG.eleDownLink)

            if (hrefele) {
                resulttext += hrefele.prop('href') + '\n'
            }
        }
    }
    GM_setClipboard(resulttext, 'text');
    $("#process-log").text('下载链接 已拷贝在剪贴板中');
}

function addAdoptColumn(html) {
    // const torTable = $(THISCONFIG.eleTorTable);
    if (THISCONFIG.host != "pterclub.com"){
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
                $(element).append('<td ><a href=/viewclaims.php?add_torrent_id=' + torid[1] + '> 认领</a></td>');
            }
        }
        else {
            $(element).append('<td class="colhead"> 认领种子 </td>');
        }
    }
}


(function () {
    "use strict";
    if (THISCONFIG) {
        addAdoptColumn(document);
        addFilterPanel();
        $("#btn-filterlist").click(function () {
            onClickFilterList(document);
        });
        $("#btn-downloadfiltered").click(function () {
            onClickDownloadFiltered(document);
        });

    }

})();
