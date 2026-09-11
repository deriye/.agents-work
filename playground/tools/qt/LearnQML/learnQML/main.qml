//import related modules
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15

Window {
    id: root
    width: 200
    height: 100
    color: "red"
    visible: true


    Rectangle {
        width: root.width / 4
        height: root.height
        color: "blue"
    }

    Rectangle {
        width: (2 * root.width) / 4
        height: root.height
        x: root.width / 4
        color: "green"
    }
}