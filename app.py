#!/usr/bin/env python

import asyncio
import json
import websockets
import random

import manager_orders as ORDS

MAX_RACK_LOCATIONS = 3
REGISTERED_RACK_LOCATIONS = {}

MAX_CART_LOCATIONS = 6
REGISTERED_CART_LOCATIONS = {}

MAX_LOCATIONS = MAX_RACK_LOCATIONS + MAX_CART_LOCATIONS


async def play_rack_locations(websocket, location_key):
    global batch_orders
    global current_item
    
    async for message in websocket:

        print("Message from  location: ", location_key )
        
        if len(REGISTERED_RACK_LOCATIONS) >= MAX_RACK_LOCATIONS:
            # Parse a "play" event from the UI.
            event = json.loads(message)
            print("from play() -- recived in websocket")
            print(event)

            assert event["type"] == "pushed"
            #
            # try:
            print("pushed the location: ", type(location_key) )
            print("current_item.loc_in_rack: ", type(current_item.loc_in_rack) )

            if location_key == current_item.loc_in_rack:
                print(" move to pick the next item ...")

                # OFF the old current_display
                event_settter_off = {
                    "type": "update",
                    "location_code": current_item.loc_in_rack,
                    "value": " ",
                    "backgroundColor" : "black"
                }

                location_socket1 = REGISTERED_RACK_LOCATIONS[current_item.loc_in_rack]
                await location_socket1.send(json.dumps(event_settter_off)) 

                print("old item: ", current_item)
                # ON the new current_display                
                current_item = batch_orders.pick_item()
                print("new item: ", current_item)

                # and send update value to the button attached
                event_settter_on = {
                    "type": "update",
                    "location_code": current_item.loc_in_rack,
                    "value": random.randint(1,20),
                    "backgroundColor" : "green"
                }
            
                location_socket2 = REGISTERED_RACK_LOCATIONS[current_item.loc_in_rack]
                await location_socket2.send(json.dumps(event_settter_on))

            # except RuntimeError as exc:
            #     # Send an "error" event if the move was illegal.
            #     await error(websocket, str(exc))
            #     continue
        else:
            print("waiting for start the picking process")

async def play_cart_locations(websocket, location_key):
    global batch_orders
    global current_item
    
    async for message in websocket:

        print("Message from  location: ", location_key )
        registered_locations = len(REGISTERED_RACK_LOCATIONS) + len(REGISTERED_CART_LOCATIONS)
        
        if registered_locations >= MAX_LOCATIONS:
            # Parse a "play" event from the UI.
            event = json.loads(message)
            print("from play() -- recived in websocket")
            print(event)

            assert event["type"] == "pushed"
            #
            # try:
            print("pushed the location: ", location_key)
            print("current_item.loc_in_cart: ", current_item.loc_in_cart )
            print("current_item.loc_in_rack: ", current_item.loc_in_rack )

            if location_key == current_item.loc_in_cart:
                print(" move to pick the next item ...")

                # OFF the old current_display
                event_settter_off = {
                    "type": "update",
                    "location_code": current_item.loc_in_rack,
                    "value": " ",
                    "backgroundColor" : "black"
                }

                location_socket1 = REGISTERED_RACK_LOCATIONS[current_item.loc_in_rack]
                await location_socket1.send(json.dumps(event_settter_off)) 
                
                location_socket11 = REGISTERED_CART_LOCATIONS[current_item.loc_in_cart]
                event_settter_off["location_code"] = current_item.loc_in_cart
                await location_socket11.send(json.dumps(event_settter_off)) 

                print("old item: ", current_item)
                # ON the new current_display                
                current_item = batch_orders.pick_item()
                print("new item: ", current_item)

                # and send update value to the button attached
                event_settter_on = {
                    "type": "update",
                    "location_code": current_item.loc_in_rack,
                    "value": random.randint(1,20),
                    "backgroundColor" : "green"
                }
            
                location_socket2 = REGISTERED_RACK_LOCATIONS[current_item.loc_in_rack]
                await location_socket2.send(json.dumps(event_settter_on))

                location_socket22 = REGISTERED_CART_LOCATIONS[current_item.loc_in_cart]
                event_settter_on["location_code"] = current_item.loc_in_cart
                await location_socket22.send(json.dumps(event_settter_on))

            # except RuntimeError as exc:
            #     # Send an "error" event if the move was illegal.
            #     await error(websocket, str(exc))
            #     continue
        else:
            print("waiting for start the picking process")


async def play(websocket, location_key):
    """
    Receive and process moves from a player.
    """
    play_cart_locations(websocket, location_key)


async def start(websocket, location_key):
    """
    Handle a connection from the first player: start a new game.
    """
    global current_item

    # Initialize a picking round, the set of WebSocket connections
    # receiving messages/pushed from this round.
    connected = websocket
    if location_key > 0 :
        REGISTERED_RACK_LOCATIONS[location_key] = connected
    elif location_key < 0 :
        REGISTERED_CART_LOCATIONS[location_key] = connected

    print("Current RACK locations registered : ", len(REGISTERED_RACK_LOCATIONS) )
    print("Current CART locations registered : ", len(REGISTERED_CART_LOCATIONS) )

    try:
        # Send the value to display to attached button in the browser of the location_code,
        event = {
            "type": "setter_location",
            "location_code": location_key
        }

        await websocket.send(json.dumps(event))

        registered_locations = len(REGISTERED_RACK_LOCATIONS) + len(REGISTERED_CART_LOCATIONS)
        
        if registered_locations >= MAX_LOCATIONS:           
            print("start picking process!!!")
            # Send the value to display to attached button in the browser of the location_code,
            
            print("item_location_rack : ", current_item.loc_in_rack)
            print("item_location_cart : ", current_item.loc_in_cart)

            event_settter = {
                "type": "update",
                "location_code": current_item.loc_in_rack,
                "value": current_item.qty,
                "backgroundColor" : "green"
            }

            rack_socket = REGISTERED_RACK_LOCATIONS[current_item.loc_in_rack]
            await rack_socket.send(json.dumps(event_settter))

            cart_socket = REGISTERED_CART_LOCATIONS[current_item.loc_in_cart]
            event_settter["location_code"] = current_item.loc_in_cart
            await cart_socket.send(json.dumps(event_settter))


        # Receive and process pushed_location from the round.
        await play_cart_locations(websocket, location_key)

    finally:
        del REGISTERED_RACK_LOCATIONS[location_key]


async def handler(websocket):
    """
    Handle a connection and dispatch it according to who is connecting.
    """
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)

    print("".center(50,"-"))
    print(event)
    print("".center(50,"-"))
    
    assert event["type"] == "init"


    if "location_code" in event:
        location_code = int(event["location_code"])
        print("setup location code : ", location_code)
        print("-"*50)
        # add location to register.
        await start(websocket, location_code)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    print("\n"*3)
    print("Pick To Light".center(50," "))
    print("SERVER ".center(50," "))
    print("log...")
    print("\n"*1)
    

    global current_item
    global batch_orders

    batch_orders =  ORDS.Manager_Picker_Orders( file_orders = "orders.csv",
                                                policy = ORDS.POLICY.BY_ORDER_SEQUENTIAL,
                                                max_orders = MAX_RACK_LOCATIONS )
    
    current_item = batch_orders.pick_item()

    asyncio.run(main())
