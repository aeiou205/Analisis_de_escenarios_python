#!/usr/bin/env python

import asyncio
import json
import websockets
import random

from manager_orders import Manager_Picker_Orders, POLICY
from motor_controller_visual_guide import Move_Motors

MAX_CART_LOCATIONS = 2
REGISTERED_CART_LOCATIONS = {}


def visual_status_locations( cart_locations ):

    cart_viewer = """ 
                |-----|-----|-----|
                | 11  | 21  |  31 | 
                |-----|-----|-----|
                | 12  | 22  |  32 | 
                |-----|-----|-----|
                Oo               oO
    """

    for loc in cart_locations:
        cart_viewer = cart_viewer.replace(str(loc), "**" )
    
    print("Registered location in RACK: ")
    print(cart_viewer)



async def play(websocket, location_key):
    """
    Receive and process moves from a player.
    """
    global batch_orders
    global current_item
    
    async for message in websocket:

        print("Message from  location: ", location_key )
        registered_locations = len(REGISTERED_CART_LOCATIONS)
        
        if registered_locations >= MAX_CART_LOCATIONS:
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
                
                cart_socket_prev_loc = REGISTERED_CART_LOCATIONS[current_item.loc_in_cart]
                event_settter_off["location_code"] = current_item.loc_in_cart
                await cart_socket_prev_loc.send( json.dumps(event_settter_off) ) 

                print("old item: ", current_item)
                # ON the new current_display                
                current_item = batch_orders.pick_item()
                print("new item: ", current_item)

                # and send update value to the button attached
                event_settter_on = {
                    "type": "update",
                    "location_code": current_item.loc_in_rack,
                    "value": current_item.qty,
                    "backgroundColor" : "green"
                }
            
                #theVisualGuide.target_location(current_item.loc_in_rack, current_item.qty)

                cart_socket_curr_loc = REGISTERED_CART_LOCATIONS[current_item.loc_in_cart]
                event_settter_on["location_code"] = current_item.loc_in_cart
                await cart_socket_curr_loc.send( json.dumps(event_settter_on) )

            # except RuntimeError as exc:
            #     # Send an "error" event if the move was illegal.
            #     await error(websocket, str(exc))
            #     continue
        else:
            print("waiting for start the picking process")

async def start(websocket, location_key):
    """
    Handle a connection from the first player: start a new game.
    """
    global current_item

    # Initialize a picking round, the set of WebSocket connections
    # receiving messages/pushed from this round.
    connected = websocket

    REGISTERED_CART_LOCATIONS[location_key] = connected

    print("Current CART locations registered : ", len(REGISTERED_CART_LOCATIONS) )

    visual_status_locations( list( REGISTERED_CART_LOCATIONS.keys())  )

    try:
        # Send the value to display to attached button in the browser of the location_code,
        event = {
            "type": "setter_location",
            "location_code": location_key
        }

        await websocket.send(json.dumps(event))

        # FIX: Update rule, throw error 
        registered_locations = len(REGISTERED_CART_LOCATIONS)
        
        if registered_locations >= MAX_CART_LOCATIONS:           
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

            cart_socket = REGISTERED_CART_LOCATIONS[current_item.loc_in_cart]
            event_settter["location_code"] = current_item.loc_in_cart
            await cart_socket.send(json.dumps(event_settter))


        # Receive and process pushed_location from the round.
        await play(websocket, location_key)

    finally:
        del REGISTERED_CART_LOCATIONS[location_key]


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
    print("Pick To Guide LASER".center(50," "))
    print("SERVER ".center(50," "))
    print("log...")
    print("\n"*1)
    

    global current_item
    global batch_orders
    global theVisualGuide

    batch_orders =  Manager_Picker_Orders( file_orders = "orders_new.csv",
                                                policy = POLICY.BY_ORDER_SEQUENTIAL,
                                                max_orders = MAX_CART_LOCATIONS )
    
    current_item = batch_orders.pick_item()

    theVisualGuide = Move_Motors(port = 'COM3', time_sleep=2)

    asyncio.run( main() )

    # while True:
    #     item = batch_orders.pick_item()

    #     if item is not None:
    #         print(item)
    #         # TODO: send command to arduino
    #     else:
    #         break
