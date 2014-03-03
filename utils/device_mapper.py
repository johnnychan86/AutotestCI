# -*- coding: utf-8 -*- 
'''
Created on 2013-12-2

@author: juliochen
'''

device = {'021WNP4C2B044626': '华为U9508',
          '3230a14cb4921077': '三星I9300',
          'HC36MW905016': 'htc one',
          'MedfieldB7A82B79': '联想K900',
          '21d2e4b1': '米2',
          '040ABFTSQC5W': 'Meizu MX2',
          '353BCHHMEAPY': 'meizu mx3',
          'EUS8LBVOW8EQKZOR': 'Vivo X1St',
          'OFWK4PO7SS4S6SI7': '红米',
          '979095ae': 'MI2S',
          '095de1b7': 'mi3',
          '4d00f511929250fd': '三星S4',
          '4d00810128d350bf': '三星S4',
          '4df0f936267d21c3': '三星Note2',
          'KVTSKV7DMBGA7TUO': 'Vivo X3t',
          'c0090430a847010': '三星SII'
          }

os_version = {'021WNP4C2B044626': '4.0.4',
      '3230a14cb4921077': '4.1.2',
      'HC36MW905016': '4.2.1',
      'MedfieldB7A82B79': '4.2.1',
      '21d2e4b1': '4.1.1',
      '040ABFTSQC5W': '4.1.2',
      '353BCHHMEAPY': '4.2.1',
      'EUS8LBVOW8EQKZOR': '',
      'OFWK4PO7SS4S6SI7': '4.2.2',
      '979095ae': '',
      '095de1b7': '4.2.1',
      '4d00f511929250fd': '4.3',
      '4d00810128d350bf': '4.3',
      '4df0f936267d21c3': '4.1.2',
      'KVTSKV7DMBGA7TUO': '',
      'c0090430a847010': '4.0.4'
      }

def get_model(id):
    if device.has_key(id):
        return device[id]
    else:
        return ''
    
def get_os(id):
    if os_version.has_key(id):
        return os_version[id]
    else:
        return ''