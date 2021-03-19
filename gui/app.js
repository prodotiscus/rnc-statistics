window.addEventListener("load", function () {
  var app = new Vue({
    el: "#app",
    data: {
      mode: "mainPage",
      query_objects: [],
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
      randomizeQuery: function (queryCommonName) {
        this.mode = "randomizer"
        this.working_on_query = queryCommonName
      },
      downloadQuery: function (queryCommonName) {
        this.mode = "downloader"
        this.working_on_query = queryCommonName
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
      },
      persistentLoading: function () {
        if (!this.run_download) return;
        (function(t) {
          $.get("/download_check_ten/" + t.working_on_query, function (d) {
          console.log(d);
          console.log(this);
          console.log(t);
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
