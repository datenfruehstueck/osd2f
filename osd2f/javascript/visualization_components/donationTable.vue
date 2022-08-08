<template>
  <b-container fluid="md">
    <div class="mb-3">
      <b-row>
        <b-col lg>
          {{content.preview_component.file_text}} <b>{{filedata.filename}}</b>
        </b-col>
        <b-col lg>
            {{content.preview_component.entries_in_file_text}} <b>{{ this.rows }}</b>
        </b-col>
        <b-col lg>
          <label for="per-page-select">{{content.preview_component.entries_per_page_text}}</label>
          <b-form-select
            class="w-50"
            id="per-page-select"
            v-model="perPage"
            :options="pageOptions"
            align="right"
            size="sm"
            ></b-form-select>
        </b-col>
      </b-row>
    </div>

    <div class="mb-3">
      <b-row>
        <b-col xl>
          <b-form-input
            v-model="search"
            :placeholder="content.preview_component.search_box_placeholder"
            ></b-form-input>
        </b-col>
        <b-col xl v-if="showfields.map(e => e[Object.keys(e)[0]].formatter != undefined).includes(true)">
          <b-form-datepicker
            v-model="startDate"
            reset-button
            today-button
            :label-today-button="content.preview_component.today_text"
            close-button
            :label-close-button="content.preview_component.close_text"
            :date-format-options="{ year: 'numeric', month: '2-digit', day: '2-digit' }"
            :placeholder="content.preview_component.startdate_text"
            value-as-date
            :max="max"
            ></b-form-datepicker>
        </b-col>
        <b-col xl v-if="showfields.map(e => e[Object.keys(e)[0]].formatter != undefined).includes(true)">
          <b-form-datepicker
            v-model="endDate"
            reset-button
            today-button
            :label-today-button="content.preview_component.today_text"
            close-button
            :label-close-button="content.preview_component.close_text"
            :date-format-options="{ year: 'numeric', month: '2-digit', day: '2-digit' }"
            :placeholder="content.preview_component.enddate_text"
            value-as-date
            :max="max"
            ></b-form-datepicker>
        </b-col>
        <b-col xl class="text-right">
          <b-button
            variant="danger"
            @click="removeSelection"
            large
            >{{content.preview_component.remove_rows_button}}</b-button>
        </b-col>
      </b-row>
    </div>
    <b-table
      id="file-table"
      responsive
      hover
      fixed
      selectable
      show-empty
      stacked="lg"
      striped
      :items="items"
      :filter="search"
      :fields="showfields"
      :current-page="currentPage"
      :per-page="perPage"
      @row-selected="onRowSelected"
      sort-icon-left>
      <template #empty="scope">
        <p style="text-align:center">{{content.preview_component.no_matches_text}}</p>
      </template>
      <template #emptyfiltered="scope">
        <p style="text-align:center">{{content.preview_component.no_matches_text}}</p>
      </template>
    </b-table>
    <div class="row justify-content-center">
      <b-pagination
        v-model="currentPage"
        aria-controls="file-table"
        :total-rows="rows"
        :per-page="perPage"
        ></b-pagination>
    </div>
  </b-container>
</template>

<script>
import {server} from '../server_interaction'
import moment from 'moment'
export default {
  props: {
    fields: Array,
    filedata: Object,
    content: Object,
  },

  created: function() {
    if (this.filedata.entries == undefined) {
      return
    }
    var fields = new Set
    for (let i=0; i < this.filedata.entries.length; i++) {
      Object.keys(this.filedata.entries[i]).forEach((f) => fields.add(f))
    }
    let showfields = new Array
    fields.forEach(f => {
      let o = new Object
      o[f] = {"label": f,
              "sortable" : true}
      if(RegExp('.*timestamp$', 'i').exec(f)) {
        o[f]['formatter'] = (value, key, item) => {
          if ((new Date(value)). getTime() > 0) {
            return moment(value, 'X').format('LLL');
          } else {
            return value;
          }
        }
      }
      showfields.push(o)
    })
    this.showfields = showfields
  },

  data() {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const maxDate = new Date(today)
    maxDate.setDate(maxDate.getDate())
    return {currentPage: 1,
            perPage: 10,
            pageOptions: [10, 25, 50, { value: 10000000, text: this.content.preview_component.show_all_text }],
            selected : null,
            search: null,
            startDate: null,
            endDate: null,
            max: maxDate}
  },

  computed: {
    rows() {
      try {
        return this.filedata.entries.length
      } catch {
        console.log("no file yet")
        return 0
      }
    },
    items() {
      if (this.filedata.entries == undefined || this.filedata.entries == null || this.filedata.entries.length == 0) {
        return []
      } else if (this.startDate != null || this.endDate != null) {
        for (let i = 0; i < this.showfields.length; i++) {
          if (RegExp('.*timestamp$', 'i').exec(this.showfields[i][Object.keys(this.showfields[i])[0]].label)) {
            return this.filedata.entries.filter(e =>
              ((moment(e[this.showfields[i][Object.keys(this.showfields[i])[0]].label], 'X').isSameOrAfter(moment(this.startDate), 'day') || this.startDate == null) &&
              (moment(e[this.showfields[i][Object.keys(this.showfields[i])[0]].label], 'X').isSameOrBefore(moment(this.endDate), 'day') || this.endDate == null)) ||
              !(new Date(e[this.showfields[i][Object.keys(this.showfields[i])[0]].label])).getTime()
            )
            break
          }
        }
        return this.filedata.entries
      }
      return this.filedata.entries
    },
  },

  methods: {
    onRowSelected(items) {
      if (items.length > 0) {
        server.log("INFO","select row", this.filedata.submission_id)
      }
      this.selected = items
    },
    removeSelection() {
      if(this.selected == null) {
        return
      }
      server.log("INFO",`removed rows`, window.sid, { rows_removed:this.selected.length })
      this.filedata.n_deleted += this.selected.length
      this.filedata.entries = this.filedata.entries.filter(e => !this.selected.includes(e))
      this.selected = null
    }
  }
}
</script>
