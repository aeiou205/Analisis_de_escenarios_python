import random

class Random_Order:
    def __init__(self, max_locations= 16, max_items_by_order=8, max_qty_by_item = 10):
        self.MAX_LOCATIONS = max_locations
        self.MAX_ITEMS_BY_ORDER = max_items_by_order
        self.MAX_QUANTITY_BY_ITEM = max_qty_by_item   

        self.current_order = 0
        self.locations = [x for x in range(1, self.MAX_LOCATIONS)]

    def __next__(self):
        self.current_order += 1
        random.shuffle(self.locations)

        num_items = random.randint( 1, self.MAX_ITEMS_BY_ORDER )
        the_order = [ 100+self.current_order, num_items ]

        for item in range(0,num_items):
            the_order.extend( [ self.locations[item],  random.randint(1, self.MAX_QUANTITY_BY_ITEM) ] )

        return the_order
    
    def __iter__(self):
        return self

class Orders_Generator:

    def __init__(self,  max_locations= 16, max_items_by_order=8, max_qty_by_item = 10):
        """ 
            Factory class to generate random orders for picking process at a warehouse

        Args:
            num_orders (int, optional):numero de ordenes a solicitar. Defaults to 3.
            max_locations (int, optional):maximo de posiciones  Defaults to 16.
            max_items_by_order (int, optional): maximos de items a tomar. Defaults to 8.
            max_qty_by_item (int, optional): max quantities by item. Defaults to 10.
        """
        self.__order =  Random_Order(max_locations, max_items_by_order, max_qty_by_item )

    def generator(self, num_orders = 10, namefile_csv = "orders.csv"):

        """simple class"""
        print("\n"*3)
        print("="*50)
        print("Orders generator".center(50," "))
        print("="*50)
        print("\n"*1)

        with open(namefile_csv, "w") as file:

            file.write( "# MAX_LOCATIONS : {}\n".format(self.__order.MAX_LOCATIONS) )
            file.write( "# MAX_ITEMS_BY_ORDER : {}\n".format(self.__order.MAX_ITEMS_BY_ORDER) )
            file.write( "# MAX_QUANTITY_BY_ITEM : {}\n".format(self.__order.MAX_QUANTITY_BY_ITEM) )

            # set the header at csv file
            header_csv = "NUM_ORDER, NUM_ITEMS"
            for ii in range(0,self.__order.MAX_ITEMS_BY_ORDER):
                header_csv += ", LOC, QTY"    
            
            print(header_csv)
            file.write(header_csv+"\n")

            for _ in range(0,num_orders):
                order = next( self.__order )
                line_csv = ",".join( str(e) for e in order ) 
                print(line_csv)
                file.write(line_csv+" \n")


def main():

    orders = Orders_Generator()
    orders.generator(num_orders=10)



if __name__ == '__main__':
    main()


