/**
 * script.js - Client-Side Interactive Logic
 *
 * Features:
 * - QR Code Scanner
 * - Barcode Scanner
 * - QR / Barcode Image Upload Detection
 * - Sample Product Quick Fill
 * - Dashboard Charts
 * - Tamper Detection Demo
 * - Blockchain Repair
 */

document.addEventListener("DOMContentLoaded", () => {
  initMobileNav();
  initAlertDismissals();
  initCodeGenerator();
  initVerificationScanner();
  initSamplePills();
  initDashboardCharts();
});


/* =============================================================
   MOBILE NAVIGATION
   ============================================================= */

function initMobileNav() {
  const toggleBtn = document.querySelector(".mobile-toggle");
  const navLinks = document.querySelector(".nav-links");

  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener("click", () => {
      navLinks.classList.toggle("open");
    });
  }
}


/* =============================================================
   FLASH ALERTS
   ============================================================= */

function initAlertDismissals() {
  document.querySelectorAll(".alert-close").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const alertBox = e.target.closest(".alert");

      if (alertBox) {
        alertBox.style.opacity = "0";
        alertBox.style.transform = "translateY(-10px)";

        setTimeout(() => {
          alertBox.remove();
        }, 250);
      }
    });
  });
}


/* =============================================================
   AUTOMATIC VERIFICATION CODE GENERATOR
   ============================================================= */

function initCodeGenerator() {
  const genBtn = document.getElementById("btn-generate-code");
  const codeInput = document.getElementById("verification_code");
  const productIdInput = document.getElementById("product_id");

  if (!genBtn || !codeInput) return;

  genBtn.addEventListener("click", () => {

    let pid = "PROD";

    if (productIdInput && productIdInput.value.trim()) {
      pid = productIdInput.value
        .trim()
        .toUpperCase()
        .replace(/[^A-Z0-9]/g, "");
    }

    const randomSegment =
      Math.random()
        .toString(36)
        .substring(2, 6)
        .toUpperCase();

    const randomSegment2 =
      Math.random()
        .toString(36)
        .substring(2, 6)
        .toUpperCase();

    const generated =
      `AUTH-${pid}-${randomSegment}-${randomSegment2}`;

    codeInput.value = generated;
  });
}


/* =============================================================
   SAMPLE PRODUCT QUICK FILL
   ============================================================= */

function initSamplePills() {

  const pills =
    document.querySelectorAll(".sample-pill");

  pills.forEach((pill) => {

    pill.addEventListener("click", (e) => {

      const code =
        e.currentTarget.getAttribute("data-code");

      const manualInput =
        document.getElementById(
          "manual-query-input"
        );

      const manualForm =
        document.getElementById(
          "manual-verify-form"
        );

      if (!manualInput || !code) return;

      manualInput.value = code;

      const manualTabBtn =
        document.querySelector(
          '[data-tab="manual"]'
        );

      if (manualTabBtn) {
        manualTabBtn.click();
      }

      manualInput.focus();

      manualInput.style.borderColor =
        "#10b981";

      setTimeout(() => {

        if (manualForm) {
          manualForm.submit();
        }

      }, 300);

    });

  });

}


/* =============================================================
   QR + BARCODE SCANNER
   ============================================================= */

let html5QrCodeScanner = null;
let cameraRunning = false;


/* -------------------------------------------------------------
   INITIALIZE VERIFICATION SCANNER
   ------------------------------------------------------------- */

function initVerificationScanner() {

  /* -----------------------------
     TAB SWITCHING
     ----------------------------- */

  const tabBtns =
    document.querySelectorAll(".tab-btn");

  const tabPanes =
    document.querySelectorAll(".tab-pane");


  tabBtns.forEach((btn) => {

    btn.addEventListener("click", () => {

      tabBtns.forEach((b) => {
        b.classList.remove("active");
      });

      tabPanes.forEach((p) => {
        p.classList.remove("active");
      });


      btn.classList.add("active");


      const targetId =
        btn.getAttribute("data-tab");


      const targetPane =
        document.getElementById(
          `tab-${targetId}`
        );


      if (targetPane) {
        targetPane.classList.add("active");
      }


      /* Stop camera when switching */
      if (
        targetId !== "camera" &&
        cameraRunning
      ) {

        stopCameraScanner();

      }

    });

  });


  /* -----------------------------
     GET ELEMENTS
     ----------------------------- */

  const readerElement =
    document.getElementById("reader");

  const startCameraBtn =
    document.getElementById(
      "btn-start-camera"
    );

  const stopCameraBtn =
    document.getElementById(
      "btn-stop-camera"
    );

  const fileInput =
    document.getElementById(
      "qr-file-input"
    );


  /* -----------------------------
     CREATE SCANNER
     ----------------------------- */

  if (
    readerElement &&
    typeof Html5Qrcode !== "undefined"
  ) {

    html5QrCodeScanner =
      new Html5Qrcode("reader");


    if (startCameraBtn) {

      startCameraBtn.addEventListener(
        "click",
        () => {

          startCameraScanner();

        }
      );

    }


    if (stopCameraBtn) {

      stopCameraBtn.addEventListener(
        "click",
        () => {

          stopCameraScanner();

        }
      );

    }

  }


  /* =========================================================
     QR + BARCODE IMAGE UPLOAD
     ========================================================= */

  if (fileInput) {

    fileInput.addEventListener(
      "change",
      async (event) => {

        if (
          !event.target.files ||
          event.target.files.length === 0
        ) {

          return;

        }


        const imageFile =
          event.target.files[0];


        /* Show scanning message */

        const uploadMessage =
          document.getElementById(
            "upload-status-msg"
          );


        if (uploadMessage) {

          uploadMessage.textContent =
            "Scanning image... Please wait.";

        }


        try {


          /* =================================================
             METHOD 1:
             BROWSER BARCODE DETECTOR
             ================================================= */

          if ("BarcodeDetector" in window) {


            let supportedFormats = [];


            try {

              supportedFormats =
                await BarcodeDetector.getSupportedFormats();

            }
            catch (err) {

              supportedFormats = [
                "qr_code",
                "ean_13",
                "ean_8",
                "code_128",
                "code_39",
                "code_93",
                "upc_a",
                "upc_e",
                "itf"
              ];

            }


            const preferredFormats = [

              "qr_code",

              "ean_13",

              "ean_8",

              "code_128",

              "code_39",

              "code_93",

              "upc_a",

              "upc_e",

              "itf"

            ];


            const usableFormats =
              preferredFormats.filter(
                format =>
                  supportedFormats.includes(
                    format
                  )
              );


            if (
              usableFormats.length > 0
            ) {

              const detector =
                new BarcodeDetector({

                  formats:
                    usableFormats

                });


              const bitmap =
                await createImageBitmap(
                  imageFile
                );


              const results =
                await detector.detect(
                  bitmap
                );


              if (
                results &&
                results.length > 0
              ) {


                const decodedText =
                  results[0].rawValue;


                if (
                  decodedText &&
                  decodedText.trim()
                ) {


                  if (uploadMessage) {

                    uploadMessage.textContent =
                      "Code detected successfully! Verifying...";

                  }


                  handleScanSuccess(
                    decodedText
                  );


                  return;

                }

              }

            }

          }


          /* =================================================
             METHOD 2:
             HTML5 QR CODE FALLBACK
             ================================================= */

          if (
            html5QrCodeScanner
          ) {


            try {


              const decodedText =
                await html5QrCodeScanner.scanFile(
                  imageFile,
                  true
                );


              if (
                decodedText &&
                decodedText.trim()
              ) {


                if (
                  uploadMessage
                ) {

                  uploadMessage.textContent =
                    "QR code detected! Verifying...";

                }


                handleScanSuccess(
                  decodedText
                );


                return;

              }


            }
            catch (qrError) {

              console.log(
                "QR fallback failed:",
                qrError
              );

            }

          }


          /* =================================================
             NO CODE FOUND
             ================================================= */

          if (
            uploadMessage
          ) {

            uploadMessage.textContent =
              "No readable QR code or barcode found.";

          }


          alert(
            "Could not detect a QR code or barcode in this image.\n\n" +
            "Please make sure:\n" +
            "1. The full QR code or barcode is visible.\n" +
            "2. The image is clear and not blurry.\n" +
            "3. There is enough lighting.\n" +
            "4. The code is not covered or damaged."
          );


        }
        catch (error) {


          console.error(
            "Image scan error:",
            error
          );


          if (
            uploadMessage
          ) {

            uploadMessage.textContent =
              "Scanning failed. Try another image.";

          }


          alert(
            "Unable to scan this image.\n\n" +
            "Please upload a clearer image containing a QR code or barcode."
          );


        }
        finally {


          /* Allow selecting same image again */

          fileInput.value = "";

        }


      }
    );

  }


}


/* =============================================================
   CAMERA SCANNER
   ============================================================= */

function startCameraScanner() {


  if (
    !html5QrCodeScanner ||
    cameraRunning
  ) {

    return;

  }


  const startBtn =
    document.getElementById(
      "btn-start-camera"
    );


  const stopBtn =
    document.getElementById(
      "btn-stop-camera"
    );


  const statusMsg =
    document.getElementById(
      "scanner-status-msg"
    );


  if (statusMsg) {

    statusMsg.textContent =
      "Requesting camera permissions...";

  }


  const scannerConfig = {

    fps: 10,

    qrbox: {
      width: 280,
      height: 280
    },

    aspectRatio: 1

  };


  html5QrCodeScanner
    .start(

      {
        facingMode: "environment"
      },

      scannerConfig,


      /* SUCCESS */

      (decodedText) => {

        handleScanSuccess(
          decodedText
        );

      },


      /* SCAN ERROR */

      () => {

        /* Normal while searching */

      }

    )


    .then(() => {


      cameraRunning = true;


      if (startBtn) {

        startBtn.style.display =
          "none";

      }


      if (stopBtn) {

        stopBtn.style.display =
          "inline-flex";

      }


      if (statusMsg) {

        statusMsg.textContent =
          "Camera active. Align the QR code inside the scanning frame.";

      }


    })


    .catch((error) => {


      console.warn(
        "Camera start error:",
        error
      );


      cameraRunning = false;


      if (statusMsg) {

        statusMsg.innerHTML =
          "<span style='color:#fb7185;'>" +
          "Camera unavailable or permission denied. " +
          "Please use image upload or manual input." +
          "</span>";

      }


    });


}


/* =============================================================
   STOP CAMERA
   ============================================================= */

function stopCameraScanner() {


  if (
    !html5QrCodeScanner ||
    !cameraRunning
  ) {

    return Promise.resolve();

  }


  const startBtn =
    document.getElementById(
      "btn-start-camera"
    );


  const stopBtn =
    document.getElementById(
      "btn-stop-camera"
    );


  const statusMsg =
    document.getElementById(
      "scanner-status-msg"
    );


  return html5QrCodeScanner
    .stop()


    .then(() => {


      cameraRunning = false;


      if (startBtn) {

        startBtn.style.display =
          "inline-flex";

      }


      if (stopBtn) {

        stopBtn.style.display =
          "none";

      }


      if (statusMsg) {

        statusMsg.textContent =
          "Camera stopped.";

      }


    })


    .catch((error) => {


      console.log(
        "Stop camera error:",
        error
      );


      cameraRunning = false;


    });


}


/* =============================================================
   SCAN SUCCESS
   ============================================================= */

function handleScanSuccess(decodedText) {


  if (
    !decodedText ||
    !decodedText.trim()
  ) {

    return;

  }


  const cleanCode =
    decodedText.trim();


  /* Stop camera before redirect */

  if (
    cameraRunning &&
    html5QrCodeScanner
  ) {

    stopCameraScanner()
      .finally(() => {

        redirectToVerification(
          cleanCode
        );

      });

  }
  else {


    redirectToVerification(
      cleanCode
    );


  }

}


/* =============================================================
   REDIRECT TO BACKEND VERIFICATION
   ============================================================= */

function redirectToVerification(code) {


  window.location.href =
    `/verify/check?query=${encodeURIComponent(
      code
    )}`;


}


/* =============================================================
   ADMIN DASHBOARD CHARTS
   ============================================================= */

function initDashboardCharts() {


  const catCanvas =
    document.getElementById(
      "categoryChart"
    );


  const statusCanvas =
    document.getElementById(
      "statusChart"
    );


  if (
    !catCanvas &&
    !statusCanvas
  ) {

    return;

  }


  if (
    typeof Chart === "undefined"
  ) {

    console.warn(
      "Chart.js is not loaded."
    );

    return;

  }


  fetch(
    "/api/dashboard-data"
  )


    .then((res) => {


      if (!res.ok) {

        throw new Error(
          "Failed to load dashboard data"
        );

      }


      return res.json();


    })


    .then((data) => {


      /* CATEGORY CHART */

      if (
        catCanvas &&
        data.categories
      ) {


        const labels =
          Object.keys(
            data.categories
          );


        const values =
          Object.values(
            data.categories
          );


        new Chart(
          catCanvas,
          {

            type: "doughnut",


            data: {

              labels:
                labels.length
                  ? labels
                  : ["No Products"],


              datasets: [

                {

                  data:
                    values.length
                      ? values
                      : [1],


                  backgroundColor: [

                    "#6366f1",

                    "#06b6d4",

                    "#10b981",

                    "#f59e0b",

                    "#ec4899",

                    "#8b5cf6"

                  ],


                  borderWidth: 0

                }

              ]

            },


            options: {

              responsive: true,

              maintainAspectRatio: false,


              plugins: {

                legend: {

                  position: "bottom",


                  labels: {

                    color:
                      "#94a3b8",

                    font: {

                      family:
                        "Inter",

                      size: 12

                    }

                  }

                }

              },


              cutout: "70%"

            }

          }
        );

      }


      /* STATUS CHART */

      if (
        statusCanvas &&
        data.statuses
      ) {


        const labels =
          Object.keys(
            data.statuses
          );


        const values =
          Object.values(
            data.statuses
          );


        new Chart(
          statusCanvas,
          {

            type: "bar",


            data: {

              labels:
                labels.length
                  ? labels
                  : ["No Scans"],


              datasets: [

                {

                  label:
                    "Scan Attempts",


                  data:
                    values.length
                      ? values
                      : [0],


                  backgroundColor:
                    labels.map(
                      (label) => {

                        return label ===
                          "VERIFIED"
                          ? "#10b981"
                          : "#f43f5e";

                      }
                    ),


                  borderRadius: 6

                }

              ]

            },


            options: {

              responsive: true,

              maintainAspectRatio: false,


              scales: {

                y: {

                  beginAtZero: true,


                  ticks: {

                    color:
                      "#64748b",

                    stepSize: 1

                  },


                  grid: {

                    color:
                      "rgba(255, 255, 255, 0.05)"

                  }

                },


                x: {

                  ticks: {

                    color:
                      "#94a3b8"

                  },


                  grid: {

                    display: false

                  }

                }

              },


              plugins: {

                legend: {

                  display: false

                }

              }

            }

          }
        );

      }


    })


    .catch((error) => {


      console.log(
        "Dashboard error:",
        error
      );


    });


}


/* =============================================================
   TAMPER DEMONSTRATION
   ============================================================= */

function triggerTamperDemo(productId) {


  const confirmed =
    confirm(

      `SIMULATION TEST:\n\n` +
      `Tamper Block for product '${productId}'?\n\n` +
      `This will modify blockchain data without re-mining ` +
      `and the integrity check will fail.`

    );


  if (!confirmed) {

    return;

  }


  fetch(
    "/api/tamper-demo",
    {

      method: "POST",


      headers: {

        "Content-Type":
          "application/json"

      },


      body:
        JSON.stringify({

          product_id:
            productId

        })

    }
  )


    .then((res) => {

      return res.json();

    })


    .then((res) => {


      alert(

        `ATTACK SIMULATED:\n${res.message}\n\n` +
        `Now verify '${productId}' to see the integrity failure.`

      );


      window.location.reload();


    })


    .catch((error) => {


      alert(
        "Failed to tamper block: " +
        error
      );


    });


}


/* =============================================================
   BLOCKCHAIN REPAIR
   ============================================================= */

function triggerRepairChain() {


  const confirmed =
    confirm(

      "Re-mine and restore all blockchain blocks?"

    );


  if (!confirmed) {

    return;

  }


  fetch(
    "/api/repair-chain",
    {

      method:
        "POST",


      headers: {

        "Content-Type":
          "application/json"

      }

    }
  )


    .then((res) => {

      return res.json();

    })


    .then((res) => {


      alert(

        `CHAIN REPAIRED:\n${res.message}`

      );


      window.location.reload();


    })


    .catch((error) => {


      alert(

        "Failed to repair chain: " +
        error

      );


    });


}