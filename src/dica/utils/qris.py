import crcmod


def generate_dynamic_qris(static_qris, amount):
    """
    Mengubah QRIS Statis menjadi QRIS Dinamis dengan menyuntikkan nominal harga.
    """
    # 1. Hapus CRC lama (4 karakter terakhir) dan tag 6304 (4 karakter sebelumnya)
    # Panjang CRC adalah 4, tag 6304 adalah 4. Total 8 karakter dari belakang.
    qris_without_crc = static_qris[:-8]

    # 2. Ubah indikator statis (010211) menjadi dinamis (010212)
    qris_without_crc = qris_without_crc.replace("010211", "010212", 1)

    # 3. Format nominal
    amount_str = str(int(amount))
    amount_len = str(len(amount_str)).zfill(2)
    tag_54 = f"54{amount_len}{amount_str}"

    # 4. Sisipkan Tag 54 sebelum Tag 58 (Country Code ID)
    # Tag 58 biasanya adalah "5802ID"
    parts = qris_without_crc.split("5802ID")
    if len(parts) != 2:
        # Fallback jika format berbeda
        return static_qris

    dynamic_qris_body = parts[0] + tag_54 + "5802ID" + parts[1] + "6304"

    # 5. Hitung CRC baru (CRC16 CCITT FALSE)
    crc16_func = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xFFFF, xorOut=0x0000)
    crc_value = crc16_func(dynamic_qris_body.encode("utf-8"))
    crc_hex = hex(crc_value)[2:].upper().zfill(4)

    # 6. Gabungkan menjadi QRIS Final
    final_qris = dynamic_qris_body + crc_hex
    return final_qris
