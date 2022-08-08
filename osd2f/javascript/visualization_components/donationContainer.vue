<template>
  <b-container fluid>
    <div v-if="donations.length>0">
      <div class="mb-3">
        <div class="row justify-content-center">
          <h4>{{content.file_indicator_text}} {{total_entries}}</h4>
        </div>
      </div>

      <div class="mb-3">
        <div class="row justify-content-center mb-3">
          <b-row>
            <b-col>
              <b-button
                pill
                variant="outline-primary"
                v-b-toggle.edit-donation>{{ content.inspect_button }}</b-button>
            </b-col>
            <b-col>
              <b-button
                pill
                variant="primary"
                @click="showConsentModal">{{ content.donate_button }}</b-button>
            </b-col>
          </b-row>
        </div>
      </div>

      <div>
        <b-collapse id="edit-donation">
          <div>
            <b-tabs content-class="mt-3" v-model="tabIndex">
              <b-tab
                :title="content.preview_component == undefined ? '' : content.preview_component.title"
                class="p-2">
                <p v-for="p in (content.preview_component == undefined ? [] : content.preview_component.explanation)">{{p}}</p>
              </b-tab>
              <div>
                <b-tab
                  v-for="fileob in donations"
                  :title="fileob.filename"
                  :key="fileob.filename"
                  lazy>
                  <donation-table
                    v-bind:filedata=fileob v-bind:content=content></donation-table>
                </b-tab>
              </div>
            </b-tabs>
          </div>
          <div class="text-center pt-3">
            <b-button
              pill
              variant="primary"
              @click="showConsentModal">{{ content.donate_button }}</b-button>
          </div>
        </b-collapse>
        <consent-confirmation
          :donations=this.donations
          :content=this.content></consent-confirmation>
      </div>
    </div>
  </b-container>
</template>

<script>
import donationTable from './donationTable'
import consentConfirmation from './consentConfirmation'
import {server} from '../server_interaction.js'

export default {
  components: {
    donationTable,
    consentConfirmation
  },
  props: {
    donations: Array,
    content: Object
  },
  updated: function() {
    server.log("INFO", "Tables shown changed", window.sid)
  },
  data() {
    return {
      tabIndex: 0
    }
  },
  computed: {
    total_entries () {
      let total = 0
      this.donations.forEach(d => total += d.entries.length)
      return total
    }
  },
  methods: {
    showConsentModal(){
      this.$bvModal.show('consent-modal')
      server.log("INFO", "Consent modal shown")
    }
  }
}
</script>