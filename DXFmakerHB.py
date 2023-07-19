import argparse
import json

class hall_bar_properties:
    
    def __init__(self,args):
        self.search_strings=[]
        self.output_coords=[]
        self.insertflag='INSERTSPOT_'
        self.BBx= float(args['bounding_box_size'].split(',')[0])/2
        if ',' in args['bounding_box_size']:
            self.BBy=float(args['bounding_box_size'].split(',')[1])/2
        else:
            self.BBy=self.BBx
        self.pad_gap=float(args['gap_size'])
        self.channel_width=float(args['main_channel_width'])
        self.channel_length=float(args['main_channel_length'])
        self.V_channel_width=float(args['V_channel_width'])
        self.V_channel_length=float(args['V_channel_width'])
        self.gap_after_V_channel=float(args['V_channel_length'])
        self.get_insertion_strings_coords('BB-x',self.BBx)
        self.get_insertion_strings_coords('BB-y',self.BBy)
        self.get_insertion_strings_coords('IPAD-x',self.BBx-self.pad_gap)
        self.get_insertion_strings_coords('IPAD-y',(self.BBy-self.pad_gap)*2/3)
        self.get_insertion_strings_coords('VPAD1-x',self.pad_gap/2)
        self.get_insertion_strings_coords('VPAD1-y',self.BBy-self.pad_gap)
        self.get_insertion_strings_coords('VPAD2-x',self.BBx-self.pad_gap)
        self.get_insertion_strings_coords('VPAD2-y',self.BBy-self.pad_gap)
        self.get_insertion_strings_coords('HBWIDTH-y',self.channel_width/2)
        self.get_insertion_strings_coords('HBLENGTH1-x',self.channel_length/2-self.V_channel_width/2)
        self.get_insertion_strings_coords('HBLENGTH2-x',self.channel_length/2+self.V_channel_width/2)
        self.get_insertion_strings_coords('HBLENGTH3-x',self.channel_length/2+self.V_channel_width/2+self.gap_after_V_channel)
        self.get_insertion_strings_coords('VHEIGHT-y',self.channel_width/2+self.V_channel_length)
        

    def get_insertion_strings_coords(self, base_string, coord_size):
        for i in range(1,5):
            self.search_strings.append(self.insertflag+base_string+'-q'+str(i))
            if '-x' in base_string:
                if i == 2 or i == 3:
                    self.output_coords.append(-coord_size)
                else:
                    self.output_coords.append(coord_size)
            elif '-y' in base_string:
                if i== 3 or i == 4:
                    self.output_coords.append(-coord_size)
                else:
                    self.output_coords.append(coord_size)
            else:
                raise ValueError('no -x- or -y- in base string')



def make_hall_bar_from_template(destination_file_name, args, template_file_name='./HBTemplate.dxf'):
    HBp=hall_bar_properties(args)

    with open(template_file_name,mode='r') as dxf_file:
        file_data=dxf_file.readlines()

    for num, line in enumerate(file_data,0):
        for i in range(len(HBp.search_strings)):
            if HBp.search_strings[i] in line:
                file_data[num]=line.replace(HBp.search_strings[i],str(HBp.output_coords[i]))

    with open(destination_file_name,'w') as write_dxf_file:
        write_dxf_file.writelines(file_data)
    return HBp.channel_width*1e-6, HBp.channel_width/HBp.channel_length

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Command Line DXF Hall Bar maker',
                                     description='''Makes simple Hall bar dxf files with given dimensions. 
                                     All units are in microns.''')
    parser.add_argument('-f','--destination_file_name',type=str, default='./DXFmakerHallBar',
                        help='''Output file name. Do not include a file extension.
                        Default is "./DXFmakerHallBar"''')
    parser.add_argument('-b','--bounding_box_size',type=str, action='store', default='1000',
                        help='''Size of the bounding box that surrounds the Hall bar.
                        This also affects the pad size as the pad edges will be a specified distance
                        from the bounding box edge.''')
    parser.add_argument('-g','--gap_size',type=str, action='store', default='50',
                        help='''Size of the gap between the pad edges and the bounding box.''')
    parser.add_argument('-w','--main_channel_width',type=str, action='store', default='14',
                        help='''Width of the Hall bar.''')
    parser.add_argument('-l','--main_channel_length',type=str, action='store', default='100',
                        help='''Center-to-center distance between voltage leads.''')
    parser.add_argument('-wv','--V_channel_width',type=str, action='store', default='4',
                        help='''Voltage lead width.''')
    parser.add_argument('-lv','--V_channel_length',type=str, action='store', default='10',
                        help='''Voltage lead length before fanning out to pads.''')
    parser.add_argument('-lg','--gap_after_V_channel',type=str, action='store', default='5',
                        help='''Gap between edge of voltage leads and beginning of fanning
                        out of the main channel to current pad.''')
    

    args = parser.parse_args()
    args=vars(args)
    print('Creating dxf file with specifications:')
    print(json.dumps(args,indent=4))
    Chwidth, factor = make_hall_bar_from_template(args['destination_file_name']+'.dxf', args)
    print('done')
    print('''The created Hall bar has a cross sectional area of {:.2e} x <conductor thickness> m^2. 
          Multiply the measured Rxx by the factor {:.2f} to get the resistivity in Ohm/Square.'''.format(Chwidth, factor))