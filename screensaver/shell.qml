pragma ComponentBehavior: Bound
import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Hyprland

ShellRoot {
  id: root
  readonly property var scenes: [
    { file: "rocinante.png", title: "ROCINANTE", detail: "CORVETTE / SOL SYSTEM" },
    { file: "tycho.png", title: "TYCHO STATION", detail: "CONSTRUCTION PLATFORM / THE BELT" },
    { file: "nauvoo.png", title: "LDSS NAUVOO", detail: "GENERATION SHIP / THE LONG JOURNEY" },
    { file: "ring.png", title: "THE RING", detail: "SOL GATE / BEYOND THE KNOWN" }
  ]
  property int sceneIndex: 0
  property real reveal: 0
  property bool armed: false
  property bool testFrame: false
  readonly property int previewSeconds: Math.max(0, Number(Quickshell.env("EXPANSE_PREVIEW_SECONDS")) || 0)

  Timer { interval: 1200; running: true; onTriggered: root.armed = true }
  Timer {
    interval: Math.max(1, root.previewSeconds) * 1000
    running: root.previewSeconds > 0
    onTriggered: Qt.quit()
  }
  SequentialAnimation {
    id: cycle
    running: !root.testFrame
    loops: Animation.Infinite
    PauseAnimation { duration: 500 }
    NumberAnimation { target: root; property: "reveal"; from: 0; to: 1; duration: 3200; easing.type: Easing.InOutCubic }
    PauseAnimation { duration: 12000 }
    NumberAnimation { target: root; property: "reveal"; from: 1; to: 0; duration: 2600; easing.type: Easing.InOutCubic }
    PauseAnimation { duration: 400 }
    ScriptAction { script: root.sceneIndex = (root.sceneIndex + 1) % root.scenes.length }
  }

  // The same app ID as the stock saver lets Omarchy keep its normal lock timer
  // and detect dismissal through the compositor's existing window events.
  Variants {
    model: Quickshell.screens
    FloatingWindow {
      id: window
      required property var modelData
      screen: modelData
      title: "Expanse Screensaver"
      color: "#000000"
      fullscreen: true
      visible: true
      implicitWidth: modelData.width
      implicitHeight: modelData.height
      onClosed: Qt.quit()

      FocusScope {
        anchors.fill: parent
        focus: true
        Keys.onPressed: function(event) { event.accepted = true; Qt.quit() }

        Image {
          id: artwork
          source: Qt.resolvedUrl("images/" + root.scenes[root.sceneIndex].file)
          visible: false
          asynchronous: true
          onStatusChanged: if (status === Image.Error) Qt.quit()
        }
        ShaderEffect {
          anchors.fill: parent
          property variant source: artwork
          property vector2d viewportSize: Qt.vector2d(width, height)
          property real imageAspect: artwork.sourceSize.height > 0 ? artwork.sourceSize.width / artwork.sourceSize.height : 1.6
          property real reveal: artwork.status === Image.Ready ? root.reveal : 0
          property real seed: root.sceneIndex + 1
          fragmentShader: Qt.resolvedUrl("pixel-dissolve.frag.qsb")
        }

        Rectangle {
          anchors.left: parent.left
          anchors.right: parent.right
          anchors.bottom: parent.bottom
          height: Math.min(230, parent.height * 0.25)
          gradient: Gradient {
            GradientStop { position: 0; color: "#00000000" }
            GradientStop { position: 1; color: "#bb000000" }
          }
          opacity: root.reveal
        }
        Column {
          anchors.left: parent.left
          anchors.bottom: parent.bottom
          anchors.margins: Math.min(48, window.width * 0.045)
          spacing: 9
          opacity: Math.max(0, (root.reveal - 0.6) / 0.4)
          Text {
            text: root.scenes[root.sceneIndex].title
            color: "#f1ddd5"
            font.family: "monospace"
            font.pixelSize: Math.min(30, window.width / 28)
            font.letterSpacing: 5
          }
          Text {
            text: root.scenes[root.sceneIndex].detail
            color: "#db7c3e"
            font.family: "monospace"
            font.pixelSize: Math.min(11, window.width / 70)
            font.letterSpacing: 2
          }
        }
        MouseArea {
          anchors.fill: parent
          hoverEnabled: true
          cursorShape: Qt.BlankCursor
          property real lastX: -1
          property real lastY: -1
          onPressed: Qt.quit()
          onWheel: Qt.quit()
          onPositionChanged: function(mouse) {
            if (root.armed && lastX >= 0 && Math.hypot(mouse.x - lastX, mouse.y - lastY) > 3) Qt.quit()
            lastX = mouse.x
            lastY = mouse.y
          }
        }
      }
    }
  }

  Connections {
    target: Hyprland
    function onRawEvent(event) {
      // Switching to another application dismisses the saver just like input.
      if (root.armed && String(event.name) === "activewindow") {
        var data = String(event.data || "")
        if (data && !data.startsWith("org.omarchy.screensaver,")) Qt.quit()
      }
    }
  }

  IpcHandler {
    target: "screensaver"
    function quit(): void { Qt.quit() }
    function status(): string {
      return JSON.stringify({ scene: root.sceneIndex, title: root.scenes[root.sceneIndex].title, reveal: root.reveal, screens: Quickshell.screens.length })
    }
    // Deterministic frame selection for previews and visual regression checks.
    function frame(index: int, amount: real): void {
      root.testFrame = true
      root.sceneIndex = Math.max(0, Math.min(root.scenes.length - 1, index))
      root.reveal = Math.max(0, Math.min(1, amount))
    }
  }
}
