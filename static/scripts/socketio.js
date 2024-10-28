document.addEventListener('DOMContentLoaded', () => {
    var socket = io();

    // Send confirmation of connection
    socket.on('connect', function() {
        socket.send("I am connected!")
        //socket.emit('my event', {data: 'I\'m connected!'});

    });

    socket.on('message', data => {
        console.log(`Message receifed: ${data}`)
        console.log("LOLOLOLOOLOL")
    })

    socket.on('some-event', data => {
        console.log(data)
        
    })
    
    function joinRoom(room) {
        console.log(room)
        socket.emit('join', {'display_name': display_name, 'room': room})
    }
});
