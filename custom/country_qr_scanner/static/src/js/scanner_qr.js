odoo.define('odoo.track_action_status',['web.core','web.ajax','web.dom_ready'], function (require) {
	"use strict";
	var ready = require('web.dom_ready');
	var ajax = require('web.ajax');

    function onScanSuccess(qrCodeMessage) {
        var resultContainer = document.getElementById('reader-results');
        var id_result = 'reader-results';
        ajax.jsonRpc("/country_qr_scanner/get_status_registration_event", 'call',{'code':qrCodeMessage}).then(function(response){
                if (response.success == true){
                    resultContainer.innerHTML
                    = "<div id="+id_result+"><img style=height:250px;width:250px src='data:image/jpeg;base64,"+response.photo+"'/><div><h1 style=text-align:center;>Socio: <span>"+response.partner+"</span></h1><br/><h2 style=text-align:center;>Estado: <span style=font-weight:600;color:green;>"+response.status+"</span></h2><br/><h2 style=text-align:center;>Nombre: "+response.name+"</h2><br/><h2 style=text-align:center;>Doc. Identidad: "+response.vat+"</h2><br/><h2 style=text-align:center;>Fecha de Escaneo: "+response.date_scanned+"</h2></div></div>";
                }else{
                    resultContainer.innerHTML
                    = "<div id="+id_result+"><img style=height:250px;width:250px src='data:image/jpeg;base64,"+response.photo+"'/><div><h1 style=text-align:center;>Socio: <span>"+response.partner+"</span></h1><br/><h2 style=text-align:center;>Estado: <span style=font-weight:600;color:red;>"+response.status+"</span></h2><br/><h2 style=text-align:center;>Nombre: "+response.name+"</h2><br/><h2 style=text-align:center;>Doc. Identidad: "+response.vat+"</h2><br/><h2 style=text-align:center;>Fecha de Escaneo: "+response.date_scanned+"</h2></div></div>";

                }
            });
    }

    function onScanError(errorMessage) {
        console.log(errorMessage);
    }

    var html5QrcodeScanner = new Html5QrcodeScanner(

        "reader", { fps: 10, qrbox: 250 });
    html5QrcodeScanner.render(onScanSuccess, onScanError);

    // This method will trigger user permissions
    Html5Qrcode.getCameras().then(devices => {
      /**
       * devices would be an array of objects of type:
       * { id: "id", label: "label" }
       */
      if (devices && devices.length) {
        var cameraId = devices[0].id;
        // .. use this to start scanning.
      }
    }).catch(err => {
      // handle err
    });

    // Create instance of the object. The only argument is the "id" of HTML element created above.
    const html5QrCode = new Html5Qrcode("reader");

    html5QrCode.start(
      cameraId,     // retreived in the previous step.
      {
        fps: 10,    // sets the framerate to 10 frame per second
        qrbox: 250  // sets only 250 X 250 region of viewfinder to
                    // scannable, rest shaded.
      },
      qrCodeMessage => {
        // do something when code is read. For example:
        html5QrCode.stop();
        console.log(`QR Code detected: ${qrCodeMessage}`);
      },
      errorMessage => {
        // parse error, ideally ignore it. For example:
        console.log(`QR Code no longer in front of camera.`);
      })
    .catch(err => {
      // Start failed, handle it. For example,
      console.log(`Unable to start scanning, error: ${err}`);
    });

    html5QrCode.stop().then(ignore => {
      // QR Code scanning is stopped.
      console.log("QR Code scanning stopped.");
    }).catch(err => {
      // Stop failed, handle it.
      console.log("Unable to stop scanning.");
    });
    });