'use strict'

// for use áfter local filtering of fields
// allows for advanced server-side anonymization
export async function apply_adv_anonymization (fileobj) {
  let url = '/adv_anonymize_file'
  if (typeof(window['content']) !== 'undefined' && window.content['survey_base_url']) {
    url = window.content['survey_base_url'] + 'adv_anonymize_file'
  }
  fileobj = await fetch(url, {
    method: 'POST',
    mode: 'same-origin',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(fileobj)
  })
    .then(response => {
      return response.json()
    })
    .catch(response => console.log(response.error))

  return fileobj.data
}

export const server = {
  log: function (level, position, sid, entry) {
    let params = {
      level: level,
      position: position,
      cb: Math.random() // to avoid caching
    }
    if (sid != undefined) {
      params['sid'] = sid
    } else {
      if (window.sid != undefined) {
        params['sid'] = window.sid
      }
    }
    if (entry != undefined) {
      params['entry'] = JSON.stringify(entry)
    }

    let url = '/log?'
    if (typeof(window['content']) !== 'undefined' && window.content['survey_base_url']) {
      url = window.content['survey_base_url'] + 'log?'
    }
    fetch(url + new URLSearchParams(params), {
      method: 'GET',
      mode: 'same-origin',
      credentials: 'same-origin'
    })
      .then(r => {})
      .catch(e => {
        console.log('Unable to log', level, position, 'due to', e)
      })
  }
}
