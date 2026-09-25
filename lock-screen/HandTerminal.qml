pragma ComponentBehavior: Bound
import QtQuick

// Original vector interpretation of Miller's illuminated acrylic hand terminal.
// The host supplies the real password field; this component never receives it.
Item {
  id: terminal
  property bool authenticating: false
  property bool failed: false
  property bool fingerprintAvailable: false
  property string fontFamily: "monospace"
  readonly property color ink: failed ? "#ef8d83" : "#e8a24d"
  signal activate()

  Canvas {
    id: chassis
    anchors.fill: parent
    onPaint: {
      var c = getContext("2d")
      c.reset()
      function line(points, color, width) {
        c.beginPath()
        c.moveTo(points[0][0], points[0][1])
        for (var i = 1; i < points.length; i++) c.lineTo(points[i][0], points[i][1])
        c.strokeStyle = color
        c.lineWidth = width || 1
        c.stroke()
      }
      function panel(x, y, w, h, cut) {
        c.beginPath()
        c.moveTo(x + cut, y)
        c.lineTo(x + w - cut, y)
        c.lineTo(x + w, y + cut)
        c.lineTo(x + w, y + h - cut)
        c.lineTo(x + w - cut, y + h)
        c.lineTo(x + cut, y + h)
        c.lineTo(x, y + h - cut)
        c.lineTo(x, y + cut)
        c.closePath()
      }
      // Clear acrylic edge, dark glass display, and chamfered metal base.
      panel(3, 3, 344, 674, 24)
      var glass = c.createLinearGradient(0, 0, 350, 680)
      glass.addColorStop(0, "rgba(41,52,57,0.92)")
      glass.addColorStop(0.45, "rgba(5,13,19,0.86)")
      glass.addColorStop(1, "rgba(33,41,44,0.95)")
      c.fillStyle = glass
      c.fill()
      c.strokeStyle = "#74807e"
      c.lineWidth = 2
      c.stroke()
      panel(10, 10, 330, 660, 20)
      c.strokeStyle = "rgba(232,162,77,0.55)"
      c.lineWidth = 1
      c.stroke()
      line([[21, 43], [329, 43]], "#e8a24d", 2)
      line([[21, 46], [329, 46]], "#573e26")
      // Seven circular engraved controls along the left edge of the glass.
      for (var j = 0; j < 7; j++) {
        var cy = 112 + j * 40
        c.beginPath()
        c.arc(34, cy, 12, 0, Math.PI * 2)
        c.strokeStyle = j === 0 ? "#e8a24d" : "#806444"
        c.stroke()
        line([[29, cy - 6], [39, cy + 6]], "#af8450")
        line([[39, cy - 6], [29, cy + 6]], "#af8450")
        if (j % 2 === 0) line([[34, cy - 8], [34, cy + 8]], "#af8450")
      }
      // Fine etched routes and the characteristic diagonal glass scratch.
      line([[63, 117], [308, 117]], "#685139")
      line([[63, 306], [308, 306], [308, 327]], "#685139")
      line([[40, 208], [99, 224], [140, 252], [220, 273]], "rgba(224,164,101,0.22)")
      line([[127, 221], [151, 253], [177, 267]], "rgba(224,164,101,0.16)")
      // Navigation graphic: etched orbital rings, not a raster screenshot.
      c.strokeStyle = "#9c713d"
      for (var r = 25; r <= 68; r += 21) {
        c.beginPath()
        c.arc(189, 218, r, 0, Math.PI * 2)
        c.stroke()
      }
      line([[106, 218], [272, 218]], "#765532")
      line([[189, 136], [189, 297]], "#765532")
      c.beginPath()
      c.arc(230, 166, 3, 0, Math.PI * 2)
      c.fillStyle = "#e8a24d"
      c.fill()
      // Compartmented telemetry at the foot of the display.
      c.strokeStyle = "#82633f"
      c.strokeRect(24, 470, 302, 92)
      line([[111, 470], [111, 562]], "#82633f")
      line([[226, 470], [226, 562]], "#82633f")
      line([[24, 499], [326, 499]], "#82633f")
      for (var k = 0; k < 13; k++) {
        var h = 8 + ((k * 17) % 35)
        c.fillStyle = "rgba(232,162,77,0.45)"
        c.fillRect(121 + k * 7, 552 - h, 3, h)
      }
      line([[236, 547], [245, 531], [254, 540], [266, 515], [281, 533], [315, 518]], "#c48c49")
      // Silver acrylic/control housing, with longitudinal grip ribs.
      var base = c.createLinearGradient(14, 570, 335, 667)
      base.addColorStop(0, "#6e7775")
      base.addColorStop(0.25, "#303b40")
      base.addColorStop(0.6, "#172227")
      base.addColorStop(1, "#687573")
      panel(14, 574, 322, 90, 16)
      c.fillStyle = base
      c.fill()
      c.strokeStyle = "#87928e"
      c.stroke()
      for (var gx = 25; gx < 326; gx += 4) {
        if (gx > 126 && gx < 224) continue
        line([[gx, 585], [gx, 650]], "rgba(175,183,166,0.24)")
      }
      c.fillStyle = "#152025"
      c.fillRect(130, 583, 90, 71)
      c.strokeStyle = "#8b9281"
      c.strokeRect(130, 583, 90, 71)
      line([[153, 607], [197, 607]], "#465651")
      var led = c.createRadialGradient(175, 573, 1, 175, 573, 28)
      led.addColorStop(0, "rgba(255,202,80,0.9)")
      led.addColorStop(1, "rgba(255,153,24,0)")
      c.fillStyle = led
      c.fillRect(146, 546, 58, 58)
      c.fillStyle = "#ffe4a0"
      c.fillRect(172, 569, 6, 5)
    }
  }

  Text {
    x: 65; y: 59
    text: "ROCINANTE"
    color: terminal.ink
    font.family: terminal.fontFamily
    font.pixelSize: 23
    font.letterSpacing: 3
  }
  Text {
    x: 66; y: 91
    text: "CREW HAND TERMINAL / 01"
    color: "#b49164"
    font.family: terminal.fontFamily
    font.pixelSize: 9
    font.letterSpacing: 1
  }
  Text {
    x: 147; y: 198; width: 84
    text: "R O C I\nLOCAL LINK"
    horizontalAlignment: Text.AlignHCenter
    color: "#e9c69a"
    font.family: terminal.fontFamily
    font.pixelSize: 11
    lineHeight: 1.7
  }
  Text {
    x: 65; y: 324
    text: terminal.failed ? "ACCESS DENIED" : (terminal.authenticating ? "VERIFYING IDENTITY" : "IDENTITY REQUIRED")
    color: terminal.ink
    font.family: terminal.fontFamily
    font.pixelSize: 12
    font.letterSpacing: 1.1
  }
  // Real password entry occupies x=31..319, y=365..425 in the host.
  Text {
    x: 26; y: 442; width: 298
    text: terminal.fingerprintAvailable ? "ENTER TO UNLOCK / TOUCH SENSOR" : "ENTER TO UNLOCK"
    horizontalAlignment: Text.AlignHCenter
    color: "#baa07d"
    font.family: terminal.fontFamily
    font.pixelSize: 9
    font.letterSpacing: 0.5
  }
  Repeater {
    model: ["LINK", "SIGNAL", "CHANNEL"]
    Text {
      required property int index
      required property string modelData
      x: [33, 120, 235][index]; y: 479
      text: modelData
      color: "#c49e6c"
      font.family: terminal.fontFamily
      font.pixelSize: 9
    }
  }
  Text {
    x: 34; y: 519
    text: "LOCAL\nREADY"
    color: "#cfab78"
    font.family: terminal.fontFamily
    font.pixelSize: 10
    lineHeight: 1.6
  }
  Rectangle {
    x: 159; y: 615; width: 32; height: 32
    radius: 16
    color: activateArea.pressed ? "#886036" : "#293737"
    border.color: "#b49b6e"
    border.width: 1
    Text {
      anchors.centerIn: parent
      text: "↵"
      color: "#e2c49a"
      font.pixelSize: 20
    }
    MouseArea {
      id: activateArea
      anchors.fill: parent
      enabled: !terminal.authenticating
      onClicked: terminal.activate()
    }
  }
}
