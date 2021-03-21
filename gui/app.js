window.addEventListener("load", function () {
  var app = new Vue({
    el: "#app",
    data: {
      mode: "mainPage",
      query_objects: [],
      query_meta: {
        query_common_name: ""
      },
      working_on_query: null,
      downloader: {
        all_matches: 0,
        downloaded: 0,
        percentage: 0,
        finished: false
      },
      run_download: true,
      navs: {
        list_navs: [],
        selected: 1
      },
      current_extraction: null,
      extraction_items: []
    },
    mounted() {
      var self = this
      $.getJSON("/load_query_objects", function(data) {
        self.query_objects = data.query_objects;
      });
    },
    methods: {
      toggleDownload: function () {
        this.run_download = !this.run_download
        if (this.run_download)
          this.persistentLoading();
      },
      randomizeQuery: function (currentQO, queryFileName) {
        this.mode = "randomizer"
        this.query_meta = currentQO
        this.working_on_query = queryFileName
      },
      downloadQuery: function (currentQO, queryFileName) {
        this.mode = "downloader"
        this.query_meta = currentQO
        this.working_on_query = queryFileName
        this.clearDownloaderObject()
        this.persistentLoading()
      },
      clearDownloaderObject: function () {
        this.downloader = {
          all_matches: 0,
          downloaded: 0,
          percentage: 0,
          finished: false
        }
        this.run_download = true;
      },
      persistentLoading: function () {
        if (!this.run_download) return;
        (function(t) {
          $.get("/download_check_ten/" + t.working_on_query, function (d) {
          if (d.all_matches) {
            t.downloader.all_matches = d.all_matches;
            t.downloader.downloaded = d.downloaded;
            t.downloader.percentage = (d.downloaded/d.all_matches*100).toFixed(2);
          }
          t.downloader.finished = d.finished;
          if (!d.finished){
            t.persistentLoading()
          }
          else {
            t.toggleDownload();
          }
        })})(this)
      },
      loadTabsByIndex: function (nav_index) {
        (function(t){
          $.get("/navs_for_extraction/" + t.current_extraction + "/" + nav_index, function (d) {
              t.navs.list_navs = d.navs
              t.navs.selected = d.selected
              t.showByNavIndex(nav_index);
          })
        })(this);
      },
      browseExt: function (ext_id) {
        this.mode = "browser";
        this.current_extraction = ext_id;
        this.loadTabsByIndex(1);
      },
      showByNavIndex: function (nav_index) {
        this.navs.selected = nav_index;
        (function(t) {
          $.get("/get_items/" + t.current_extraction + "/" + nav_index, function (d) {
            t.extraction_items = d.items;
          })
        })(this)
      },
      toggleSelection: function (j, k) {
        this.extraction_items[k].checked = !this.extraction_items[k].checked;
        this.submitSelection(j, this.extraction_items[k].checked)
      },
      submitSelection: function (globalIndex, selectedBool) {
        command = (selectedBool ? "select" : "unselect");
        $.get("/change_selection/" + this.current_extraction + "/" + globalIndex + "/" + command,
        function (d) {

        })
      }
    }

  })
})
