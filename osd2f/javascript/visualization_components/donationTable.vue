<template>
  <b-container fluid="md">
    <div class="mb-3">
      <b-row>
        <b-col lg>
          {{"File: "}} <b>{{filedata.filename }}</b>
        </b-col>
        <b-col lg>
            {{content.preview_component.entries_in_file_text}} <b>{{ this.rows }}</b>
        </b-col>
        <b-col lg>
          <label for="per-page-select">Einträge pro Seite: </label>
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
        <b-col xl>
          <b-form-datepicker
            v-model="startDate"
            reset-button
            today-button
            label-today-button="Heute"
            close-button
            label-close-button="Schließen"
            :date-format-options="{ year: 'numeric', month: '2-digit', day: '2-digit' }"
            placeholder="Startdatum eingeben"
            value-as-date
            :max="max"
            ></b-form-datepicker>
        </b-col>
        <b-col xl>
          <b-form-datepicker
            v-model="endDate"
            reset-button
            today-button
            label-today-button="Heute"
            close-button
            label-close-button="Schließen"
            :date-format-options="{ year: 'numeric', month: '2-digit', day: '2-digit' }"
            placeholder="Enddatum eingeben"
            value-as-date
            :max="max"
            ></b-form-datepicker>
        </b-col>
        <b-col xl>
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
        <p style="text-align:center">Es konnten keine übereinstimmenden Ergebnisse gefunden werden</p>
      </template>
      <template #emptyfiltered="scope">
        <p style="text-align:center">Es konnten keine übereinstimmenden Ergebnisse gefunden werden</p>
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

    // infer fields from entries
    created: function(){
        if (this.filedata.entries == undefined){return}
      var fields = new Set
      for (let i=0; i<this.filedata.entries.length; i++){
          Object.keys(this.filedata.entries[i]).forEach((f)=>fields.add(f))
      }
      let showfields = new Array
      fields.forEach(f => {
          let o = new Object
          o[f] = {
              "label": f,
              "sortable" : true
              }
          showfields.push(o)}
          )

      this.showfields = showfields
    },
    data(){
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const maxDate = new Date(today)
    maxDate.setDate(maxDate.getDate())
        return {
            currentPage: 1,
            perPage: 5,
            pageOptions: [5, 25, 50, { value: 10000000000000, text: "Alles anzeigen" }],
            selected : null,
            search: null,
            startDate: null,
            endDate: null,
            max: maxDate
        }
    },

    computed: {

        rows(){
         try {
             return this.filedata.entries.length
         } catch {
             console.log("no file yet")
             return 0
         }
        },
        items(){
            if (this.filedata.entries == undefined || this.filedata.entries==null){
                return []
            }
            else if (this.startDate != null || this.endDate != null){
              return this.filedata.entries.filter(e =>
        moment(e.timestamp).isSameOrAfter(moment(this.startDate), 'day') && moment(e.timestamp).isSameOrBefore(moment(this.endDate), 'day') ||
        this.startDate == null && moment(e.timestamp).isSameOrBefore(moment(this.endDate), 'day') ||
        this.endDate == null && moment(e.timestamp).isSameOrAfter(moment(this.startDate), 'day'))
            }
            return this.filedata.entries

        },

        },

    methods: {
        onRowSelected(items){
            if (items.length>0){server.log("INFO","select row", this.filedata.submission_id)}
            this.selected = items
        },
        removeSelection(){
            if(this.selected==null){return}
            server.log("INFO",`removed rows`, window.sid, {rows_removed:this.selected.length})
            this.filedata.n_deleted += this.selected.length
            this.filedata.entries = this.filedata.entries.filter(e => !this.selected.includes(e))
            this.selected = null
        },
    }
}
</script>
