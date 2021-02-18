'use strict'

import Vue from 'vue'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import donationTable from './visualization_components/donationTable'
import donationContainer from './visualization_components/donationContainer'

// Import Bootstrap an BootstrapVue CSS files (order is important)
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.use(BootstrapVue, IconsPlugin)

var app = new Vue({
  el: '#visualization',
  components: {
    'donation-table': donationTable,
    'donation-container': donationContainer
  },
  data: {
    filedata: {},
    fields: [],
    donations: []
  }
})

// Placeholder visualization
export function visualize (d) {
  //d.forEach(appendFile);
  //app.filedata = mockdata[0]
  app.donations = d
}

function appendFile (fileobj) {
  document.getElementById(
    'files'
  ).innerHTML += `<p>${fileobj.filename} : <b> ${fileobj.entries.length} </b> datapoints</p>`
}
