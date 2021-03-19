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
      run_download: true
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
      }
    }
  })
})
