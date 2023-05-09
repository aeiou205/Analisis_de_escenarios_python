from collections import namedtuple
import csv

class POLICY:
    BY_ORDER_SEQUENTIAL = 0
    BY_ORDER_ROW_MAJOR = 1
    BY_ORDER_COLUMN_MAJOR = 2
    BATCHING_ROW_MAJOR = 3
    BATCHING_COLUMN_MAJOR = 4

Item = namedtuple("Item", "id_order loc_in_cart loc_in_rack qty")

class Order:
    id = None
    loc_pick_car = None
    qty_items = None
    list_items = []

    def __init__(self, line_order, loc_pick_car) -> None:
        self.id = int(line_order[0])
        self.qty_items = int(line_order[1])
        self.list_items = []
        self.loc_pick_car = loc_pick_car

        skip = 2
        for ii in range(0,self.qty_items):
            self.list_items.append( (int(line_order[skip+ii*2]), int(line_order[skip+ii*2+1])) ) 

    def print_order(self):
        print("-"*20)
        print("ID_ORDER: ", self.id)
        print("loc_pick_car: ", self.loc_pick_car)
        print("#items: ", self.qty_items)
        print(self.list_items)

class List_Items:
    __list_items = None

    def __init__(self, list_items):
        self.__list_items = list_items

    def __iter__(self):
        self.idx_curr_item = 0
        return self

    def __next__(self):
        if self.idx_curr_item < len(self.__list_items):
            item = self.__list_items[ self.idx_curr_item ]
            self.idx_curr_item += 1
            return item
        else:
            None

class Batching_Orders:
    __policy = None
    __list_orders = []
    __batch_items = []
    __iter_items = None

    def __init__(self, list_orders, policy ) -> None:
        self.__policy = policy
        self.__list_orders = list_orders

        self.__batch_items = self.__batching( self.__policy, self.__list_orders)
        self.__iter_items = iter( List_Items(self.__batch_items) )

    def __batching( self, policy, orders ):
        batching_by_policy = { 
            POLICY.BY_ORDER_SEQUENTIAL : self.__batching_by_order_sequential,
            POLICY.BY_ORDER_ROW_MAJOR : None,
            POLICY.BY_ORDER_COLUMN_MAJOR : None,
            POLICY.BATCHING_ROW_MAJOR : None,
            POLICY.BATCHING_COLUMN_MAJOR : None
        }

        list_items = batching_by_policy[ policy ]( orders )

        return list_items

    def __batching_by_order_sequential(self, orders):
        batch_items = []
        for order in orders:
            for location_in_rack, qty_items in order.list_items:
                batch_items.append( Item(order.id, order.loc_pick_car, location_in_rack, qty_items) )
                
        return batch_items

    def get_iterator_items(self):
        return self.__iter_items

    def print_items(self):
        print(self.__batch_items)

class Manager_Picker_Orders:
    __list_Orders = []
    __max_orders = None
    __policy = None
    __iter_items = None
    
    def __init__(self, file_orders, policy = POLICY.BY_ORDER_SEQUENTIAL, max_orders=6) -> None:

        self.__max_orders = max_orders
        self.__policy = policy
        self.__list_Orders = self.load_orders_from_CSV( file_orders )

        batch_orders = Batching_Orders( self.__list_Orders, self.__policy )
        self.__iter_items = batch_orders.get_iterator_items()

    def load_orders_from_CSV(self,file_name):

        cart_keys = {  0: 11,
                        1: 12,
                        2: 21,
                        3: 22,
                        4: 32,
                        5: 32
                    }

        list_Orders = []

        print("Loading orders ...",end="")
        with open(file_name, 'r', newline='', encoding="cp437", errors='ignore') as file:
                reader_csv = csv.reader(file)
                for fila in reader_csv:
                        if fila[0][0] in ["#", "N"] :
                            continue

                        if len(list_Orders) < self.__max_orders:
                            order = Order( fila, cart_keys[ len(list_Orders) ] )
                            list_Orders.append( order )
                            # order.print_order()
                        else:
                            print("\n\t\tWARNING: MAX orders Loaded...skip the rest.....")
                            break

        print("... done")
        return list_Orders 

    def get_num_orders(self):
        return len( self.__list_Orders )
    
    def pick_item(self):
        return next( self.__iter_items )


def main():
    print("\n"*3)
    print("Manager orders".center(50," "))
    print("\n"*1)

    manager_orders =  Manager_Picker_Orders( "orders_new.csv" )

    while True:
        item = manager_orders.pick_item()

        if item is not None:
            print(item)
            # TODO: send command to arduino
        else:
            break


if __name__ == "__main__":
    main()
