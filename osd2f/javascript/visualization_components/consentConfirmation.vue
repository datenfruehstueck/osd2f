<template>
    <div>
        <b-modal 
            :title="content.consent_popup.title"
            id="consent-modal" 
            :ok-title="content.consent_popup.accept_button"
            ok-variant="success"
            :cancel-title="content.consent_popup.decline_button"
            :ok-disabled="this.processing"
            @ok="sub"
        >
            <b-overlay :show="show" rounded="sm">
                <div :aria-hidden="show ? 'true' : null">
                    <div class="p-1"> {{ content.consent_popup.lead }} </div>
                    <ul>
                        <li v-for="lit in content.consent_popup.points"> {{lit}} </li>
                    </ul>

                    <div class="p-1"> {{ content.consent_popup.end_text }} </div>
                </div>
            </b-overlay>
        </b-modal>
    </div>
</template>
<script>
import {server} from "../server_interaction"

export default {
    props:{
        donations : Array,
        content: Object
    },
    data(){
        return {
            show: false,
            processing : false
            }
    },
    computed: {
        n_entries() {
            let total = 0
            this.donations.forEach(d=>total+=d.entries.length)
            return total
        }
    },
    methods:{
        sub(evt){
            evt.preventDefault()
            this.show = true
            this.processing = true

            server.log("INFO", "consent given, uploading file")

            let url = '/upload'
            if (typeof(window['content']) !== 'undefined' && window.content['survey_base_url']) {
                url = window.content['survey_base_url'] + 'upload'
            }
            fetch(url, {
                method: 'POST',
                //mode: 'same-origin',
                mode: 'no-cors',
                //credentials: 'same-origin',
                credentials: 'omit',
                headers: {
                'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.donations)
            })
            .then(() => {
                let callback_files = {}
                if (window.content != undefined && window.content['survey_js_callback'] != undefined) {
                    for (let i = 0; i < this.$parent.$parent.donations.length; i++) {
                        callback_files[this.$parent.$parent.donations[i].filename] = {
                            'n_donated': this.$parent.$parent.donations[i].entries.length,
                            'n_deleted': this.$parent.$parent.donations[i].n_deleted
                        }
                    }
                }

                // remove processing queue
                this.processing = false
                noDonationYet = false
                this.show = false
                this.$bvModal.hide("consent-modal")
                this.$parent.$parent.donations = []
                document.getElementById('thankyou').classList.remove('invisible')

                // in survey mode, call callback function
                if (window.content != undefined  && window.content['survey_js_callback'] != undefined) {
                    let callback_function = window[window.content['survey_js_callback']]
                    if (typeof(callback_function) == 'function') {
                        callback_function(true, "", callback_files)
                    }
                }
            })
            .catch(error => {
                console.log('Error', error)
                server.log("ERROR", "failed to upload file")

                // in survey mode, call callback function
                if (window.content != undefined && window.content['survey_js_callback'] != undefined) {
                    let callback_function = window[window.content['survey_js_callback']]
                    if (typeof(callback_function) == 'function') {
                        callback_function(false, error)
                    }
                }
            })

        }
    }

}
</script>