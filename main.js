var LOCATION_CODE = 0 //  CODE  > 0  for RACK; CODE < 0 for CART
var TURN_STATUS = false

function initGame(websocket) {

  websocket.addEventListener("open", () => {

    // Send an "init" event according to who is connecting.
    const params = new URLSearchParams(window.location.search);
    let event = { type: "init" };

    if (params.has("location_code")) {
      // Second player joins an existing game.
      event.location_code = params.get("location_code");
      LOCATION_CODE = event.location_code
    }

    console.log("LOCATION_CODE is set to:" );
    console.log(LOCATION_CODE );
    websocket.send(JSON.stringify(event));

  });
}

function showMessage(message) {
  window.setTimeout(() => window.alert(message), 50);
}


function receiveMoves(websocket) {
  websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data);

    console.log("event.type")
    console.log(event.type)

    switch (event.type) {
      case "update" :
        console.log("update the display to : ");
        console.log(event.value);
        console.log("in location : ");
        console.log(event.location_code);

        TURN_STATUS = true;
        const picking = document.querySelector(".picking");
        picking.style.backgroundColor = event.backgroundColor;
        picking.textContent = event.value

        break;

    case "setter_location" :
          // TODO: update the UI to display the value to picking
          console.log("done set location to : ")
          console.log(event.location_code)
          console.log("value : ")
          console.log(event.value)

          const location = document.querySelector(".location_id");
          location.textContent =  "L " + event.location_code

          const pic = document.querySelector(".picking");
          pic.textContent =  " "

          break;

      case "error" :
        showMessage(event.message);
        break;

      default:

        throw new Error(`Unsupported event type: ${event.type}.`);
    }
  });
}


function sendMoves(websocket) {

  // When clicking a active location, send a "pushed" event for a move in that column.
  const picking = document.querySelector(".picking");

  picking.addEventListener("click", ({ target }) => {

    const event = {
      type: "pushed",
      location: LOCATION_CODE,
    };

    console.log( "on_click picking ..." )
    console.log( event )

    if( TURN_STATUS == true ){
       // picking.style.backgroundColor= "black";
       // picking.textContent = " "
       websocket.send(JSON.stringify(event));

       TURN_STATUS = false
    }

  });

}


window.addEventListener("DOMContentLoaded", () => {

      // Open the WebSocket connection and register event handlers.
      //WARNNIG: set the URL to server!!!
      const websocket = new WebSocket("ws://localhost:8001/");

      initGame(websocket);
      receiveMoves(websocket);
      sendMoves(websocket);

});
