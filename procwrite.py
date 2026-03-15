import struct, os, getpid

curpid = getpid.getpid()

def getBaseAddessFromMapsFile():
    try:
        with open("/proc/%s/maps" % curpid, "r") as f:
            lines = [line.rstrip() for line in f]
            data = lines[0].split('-')
            return data[0]
    except PermissionError:
            print("Błąd: Potrzebujesz uprawnień roota!")
            
base_address = int(getBaseAddessFromMapsFile(), 16)
offset = 0x960
start_main = 0x918

target_mem_address = base_address + offset
destination_address = base_address + start_main

def generate_arm64_jump(target_addr):
    # LDR X16, #8 (Ładuje 8 bajtów adresu z pamięci tuż za instrukcjami)
    instr_ldr = 0x58000050 
    # BR X16 (Skok do adresu w rejestrze X16)
    instr_br = 0xD61F0200 
    
    # Składanie w formacie Little-Endian (typowe dla ARM64)
    payload = struct.pack('<I', instr_ldr)  # 4 bajty
    payload += struct.pack('<I', instr_br)   # 4 bajty
    payload += struct.pack('<Q', target_addr) # 8 bajtów (adres 64-bit)
    return payload


def write_to_other_process(address, data): 
    if curpid == None:
        print("Określenie PIDa się nie powiodło")
    else:
        # Otwieramy pamięć innego procesu jako plik binarny
        try:
            with open("/proc/%s/mem" % curpid, "wb") as f:
                f.seek(address)
                f.write(data)
            print("Patch wstrzyknięty!")
        except PermissionError:
            print("Błąd: Musisz uruchomić skrypt jako ROOT (sudo)!")

# Użycie:
# pid = 1234 (sprawdź w 'ps aux' lub 'pidof main')
# write_to_other_process(pid, target_address, jump_payload)

jump_payload = generate_arm64_jump(destination_address)

if __name__ == '__main__':
    write_to_other_process(target_mem_address, jump_payload)