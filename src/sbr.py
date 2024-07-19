#! /usr/bin/env python3

 #  ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ 
 # |______|______|______|______|______|______|______|______|______|______|______|______|______|______|______|______|______| 
 #        _        ___  _      _      _____  ____   
 #       (_)      / _ \| |    | |    |  __ \|  _ \  
 #  __  ___  __ _| | | | |    | |    | |  | | |_) | 
 #  \ \/ / |/ _` | | | | |    | |    | |  | |  _ <  
 #   >  <| | (_| | |_| | |____| |____| |__| | |_) | 
 #  /_/\_\_|\__,_|\___/|______|______|_____/|____/                                                                                                                   
 #  ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ 
 # |______|______|______|______|______|______|______|______|______|______|______|______|______|______|______|______|______|

import lldb
import os
import shlex
import optparse
import json
import re
import utils


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand(
    'command script add -f sbr.handle_command sbr -h "[usage] sbr -m module -o offset"')
    # print('========')
    # print('[sbr]: set breakpoint of module by offset')
    # print('\tsbr -m module -o offset')
                    
def handle_command(debugger, command, exe_ctx, result, internal_dict):
    command_args = shlex.split(command, posix=False)
    parser = generate_option_parser()
    try:
        (options, _) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return
        
    _ = exe_ctx.target
    _ = exe_ctx.thread
    
    if options.module and options.offset:
        module = get_module_by_name(debugger, str(options.module))
        if not module:
            result.AppendMessage(str('module: %s not found' % options.module))
            return

        base_addr = get_module_base_address(debugger, module)
        if not base_addr:
            result.AppendMessage(str('module: %s not loaded?' % options.module))
            return

        offset = 0
        try:
            offset = int(options.offset, 10)
        except:
            try:
                offset = int(options.offset, 16)
            except:
                result.AppendMessage(str('offset: %s not valid.' % options.offset))
                return

        lldb.debugger.HandleCommand('image lookup --address %d' % (base_addr + offset))
        lldb.debugger.HandleCommand('breakpoint set --address %d' % (base_addr + offset))
        return
        
    result.AppendMessage(str('usage: sbr -m module -o offset'))
    return 


def get_module_by_name(debugger, moduleName):
    target = debugger.GetSelectedTarget()
    for module in target.module_iter():
        if module.file.fullpath.endswith(moduleName):
            return module
    return None

def get_module_base_address(debugger, module):
    header_addr = module.GetObjectFileHeaderAddress()
    if not header_addr.IsValid():
        return None

    load_addr = header_addr.GetLoadAddress(debugger.GetSelectedTarget())
    if load_addr != lldb.LLDB_INVALID_ADDRESS:
        return load_addr

    return header_addr.GetSection().GetFileAddress()


def generate_option_parser():
    usage = "usage: sbr -m module -o offset'"
    parser = optparse.OptionParser(usage=usage, prog="lookup")

    parser.add_option("-m", "--module",
                        action="store",
                        default=None,
                        dest="module",
                        help="module name")
                        
    parser.add_option("-o", "--offset",
                        action="store",
                        default=None,
                        dest="offset",
                        help="module offset")

    return parser
