window.addEventListener("load", function () {
  var app = new Vue({
    el: "#app",
    data: {
      mode: "mainPage",
      query_objects: [],
      working_on_query: null
    },
    mounted() {
      var self = this
      $.getJSON("/load_query_objects", function(data) {
        self.query_objects = data.query_objects;
      });
    },
    methods: {
      randomizeQuery: function (queryCommonName) {
        this.mode = "randomizer"
        this.working_on_query = queryCommonName
      }
    }
  })
})
