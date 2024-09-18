/* global moment, alert, FormData */

$(document).ready(function () {
    const csrftoken = $('[name=csrfmiddlewaretoken]').val()

    function csrfSafeMethod (method) {
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method))
    }

    $.ajaxSetup({
      beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader('X-CSRFToken', csrftoken)
        }
      }
    })

    // window.selectedMessagingChannel = $(this).attr('id').replace('message_box_', '')

    const toggleSend = function () {
      const phone = $('#phone_number').val()
      const message = $('#loopback_message').val().trim()

      const attachment = $('#loopback_attachment')[0].files[0]

      if (attachment === undefined && (message.length === 0 || phone.length === 0)) {
        $('#loopback_send_button').prop('disabled', true)
      } else {
        $('#loopback_send_button').prop('disabled', false)
      }
    }

    const updateCount = function () {
      const message = $('#loopback_message').val().trim()

      $('#loopback_character_count').html('Length: ' + message.length)

      if (message.length >= 140) {
        $('#loopback_character_count').addClass('text-danger')
      } else {
        $('#loopback_character_count').removeClass('text-danger')
      }
    }

    $('#loopback_message').on('keydown change', function (event) {
      if (event.key === 'Enter') {
        event.preventDefault()

        $('#loopback_send_button').click()
      } else {
        toggleSend()
        updateCount()
      }
    })

    $('#loopback_send_button').click(function (eventObj) {
      eventObj.preventDefault()

      const message = $('#loopback_message').val().trim()
      const phone = $('#phone_number').val() // .replace(/[^\d]/g, '');

      const attachment = $('#loopback_attachment')[0].files[0]

      const formData = new FormData()

      formData.append('From', phone)
      formData.append('LoopbackMessage', message)
      formData.append('To', window.selectedMessagingChannel)
      formData.append('attachment', attachment)

      $.ajax({
        url: 'incoming',
        type: 'POST',
        success: function (data) {
          $('#loopback_message').val('')
          $('#loopback_attachment').val('')
          $('#loopback_upload_button').html('backup')

          updateCount()
        },
        data: formData,
        cache: false,
        processData: false,
        contentType: false,
        enctype: 'multipart/form-data'
      })
    })

    $('#loopback_upload_button').click(function (eventObj) {
        $('#loopback_attachment').click()
      })

      $('#loopback_attachment').on('change', function (e) {
        if (this.files[0].size > 5 * 1024 * 1024) {
          alert('Cannot send a file larger than 5 MB. Please select another.')
          $(this).val('')
        } else {
          $('#loopback_upload_button').html('cloud_done')

          toggleSend()
        }
      })

    updateCount()
  })
