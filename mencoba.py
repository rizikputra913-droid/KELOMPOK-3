# ================================================== josss
# KODE DIPERBAIKI & SUDAH BENAR
# ==================================================

from dataclasses import dataclass  # <-- Tadi salah ketik "gitfrom", sudah aku benerin
from typing import Optional, List, Dict, Tuple
import numpy as np
import time
import random

# Kunci reproducibility
np.random.seed(31)
random.seed(31)

# Data konfigurasi
PRODI = ['Teknik Elektro', 'Informatika', 'Mesin', 'Sipil', 'Kimia']
GRADE_MAP = {
    'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'D': 1.0, 'E': 0.0
}

@dataclass
class Mahasiswa:
    nim: str
    nama: str
    prodi: str
    angkatan: int
    status: int = 0
    ipk: float = 0.0

@dataclass
class NilaiMatkul:
    kode_mk: str
    nama_mk: str
    sks: int
    grade: str
    semester: int

# ====================== DOUBLY LINKED LIST ======================
class DLLNode:
    def __init__(self, data=None):
        self.data = data
        self.prev = None
        self.next = None

class TranskripNilai:
    """Double Linked List untuk simpan riwayat nilai per semester"""
    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def tambah_nilai(self, nilai) -> None:
        """Sisip di akhir. Big-O: O(1)"""
        new_node = DLLNode(nilai)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    def hapus_terakhir(self) -> Optional[NilaiMatkul]:
        """Hapus dari akhir. Big-O: O(1)"""
        if self.tail is None:
            return None
        data = self.tail.data
        if self.head == self.tail:
            self.head = None
            self.tail = None
        else:
            self.tail = self.tail.prev
            self.tail.next = None
        self._size -= 1
        return data

    def semester_ke(self, sem: int) -> List[NilaiMatkul]:
        """Filter nilai semester tertentu. Big-O: O(n)"""
        hasil = []
        curr = self.head
        while curr:
            if curr.data.semester == sem:
                hasil.append(curr.data)
            curr = curr.next
        return hasil

    def hitung_ipk(self) -> float:
        """Hitung IPK seluruh nilai. Big-O: O(n)"""
        total_bobot = 0.0
        total_sks = 0
        curr = self.head
        while curr:
            n = curr.data
            total_bobot += GRADE_MAP[n.grade] * n.sks
            total_sks += n.sks
            curr = curr.next
        return round(total_bobot / total_sks, 2) if total_sks > 0 else 0.0

    def __len__(self):
        return self._size

# ====================== STACK ======================
class Stack:
    def __init__(self):
        self.top = None
        self._size = 0

    def is_empty(self):
        return self.top is None

    def push(self, data) -> None:
        """Tambah atas. Big-O: O(1)"""
        new_node = DLLNode(data)
        if not self.is_empty():
            new_node.next = self.top
            self.top.prev = new_node
        self.top = new_node
        self._size += 1

    def pop(self):
        """Ambil atas & hapus. Big-O: O(1)"""
        if self.is_empty():
            return None
        data = self.top.data
        self.top = self.top.next
        if self.top:
            self.top.prev = None
        self._size -= 1
        return data

# ====================== BINARY SEARCH TREE ======================
class BSTNodeMhs:
    def __init__(self, mhs: Mahasiswa):
        self.mhs = mhs
        self.transkrip = TranskripNilai()
        self.left = None
        self.right = None

class BSTMahasiswa:
    """BST berdasar NIM sebagai kunci"""
    def __init__(self):
        self.root = None

    def insert(self, mhs: Mahasiswa) -> None:
        """Sisip berdasar NIM. Big-O rata-rata O(log n), terburuk O(n)"""
        def _insert(node, mhs):
            if node is None:
                return BSTNodeMhs(mhs)
            if mhs.nim < node.mhs.nim:
                node.left = _insert(node.left, mhs)
            elif mhs.nim > node.mhs.nim:
                node.right = _insert(node.right, mhs)
            return node
        self.root = _insert(self.root, mhs)

    def search(self, nim: str) -> Optional[BSTNodeMhs]:
        """Cari berdasar NIM. Big-O rata-rata O(log n)"""
        def _search(node, nim):
            if node is None or node.mhs.nim == nim:
                return node
            if nim < node.mhs.nim:
                return _search(node.left, nim)
            return _search(node.right, nim)
        return _search(self.root, nim)

    def update_ipk(self, nim: str) -> bool:
        """Hitung ulang & simpan IPK. Big-O O(log n) + O(n_transkrip)"""
        node = self.search(nim)
        if node:
            node.mhs.ipk = node.transkrip.hitung_ipk()
            return True
        return False

    def inorder(self) -> List[Mahasiswa]:
        """Traversal naik berdasar NIM. Big-O O(n)"""
        hasil = []
        def _inorder(node):
            if node:
                _inorder(node.left)
                hasil.append(node.mhs)
                _inorder(node.right)
        _inorder(self.root)
        return hasil

    def range_ipk(self, low: float, high: float) -> List[Mahasiswa]:
        """Filter IPK di rentang nilai. Big-O O(n)"""
        return [m for m in self.inorder() if low <= m.ipk <= high]

# ====================== GRAPH DAG ======================
class GraphPrereq:
    """Graph berarah tidak siklik untuk prasyarat mata kuliah"""
    def __init__(self):
        self.adj: Dict[str, List[str]] = {}      # kode -> daftar prasyarat
        self.nama_mk: Dict[str, str] = {}         # kode -> nama matkul

    def tambah_matkul(self, kode: str, nama: str) -> None:
        if kode not in self.adj:
            self.adj[kode] = []
            self.nama_mk[kode] = nama

    def tambah_prasyarat(self, mk: str, prasyarat: str) -> None:
        """Tambah relasi A -> B (A prasyarat B). Big-O O(1)"""
        if mk in self.adj and prasyarat in self.adj:
            self.adj[mk].append(prasyarat)

    def topological_sort(self) -> List[str]:
        """Urutkan matkul valid pakai algoritma Kahn. Big-O O(V+E)"""
        in_degree = {u:0 for u in self.adj}
        for u in self.adj:
            for v in self.adj[u]:
                in_degree[v] += 1

        antrian = []
        for n, d in in_degree.items():
            if d == 0:
                antrian.append(n)
        hasil = []

        while antrian:
            u = antrian.pop(0)
            hasil.append(u)
            for v in self.adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    antrian.append(v)
        return hasil if len(hasil) == len(self.adj) else []

    def prasyarat_terpenuhi(self, node_mhs: BSTNodeMhs, kode_mk: str) -> bool:
        """Cek apakah semua prasyarat sudah lulus (nilai >= C). Big-O O(derajat)"""
        if kode_mk not in self.adj:
            return False
        prasyarat = self.adj[kode_mk]
        # ambil semua nilai transkrip
        semua_nilai = []
        curr = node_mhs.transkrip.head
        while curr:
            semua_nilai.append(curr.data)
            curr = curr.next

        lulus = {n.kode_mk: GRADE_MAP[n.grade] >= 2.0 for n in semua_nilai}
        return all(lulus.get(p, False) for p in prasyarat)

# ====================== SORTING UNTUK PERINGKAT ======================
def merge_sort_ll(head):
    """Merge Sort pada Linked List berdasar IPK menurun. Big-O O(n log n)"""
    if not head or not head.next:
        return head
    def get_mid(h):
        slow, fast = h, h.next
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        tengah = slow.next
        slow.next = None
        return tengah
    def merge(a,b):
        dummy = DLLNode()
        curr = dummy
        while a and b:
            if a.data.ipk >= b.data.ipk:
                curr.next = a
                a.prev = curr
                a = a.next
            else:
                curr.next = b
                b.prev = curr
                b = b.next
        if a:
            curr.next = a
            a.prev = curr
        if b:
            curr.next = b
            b.prev = curr
        return dummy.next
    mid = get_mid(head)
    kiri = merge_sort_ll(head)
    kanan = merge_sort_ll(mid)
    return merge(kiri, kanan)

# ====================== GENERATOR DATA ======================
def generate_mahasiswa(n=60) -> List[Mahasiswa]:
    daftar = []
    for i in range(1, n+1):
        nim = f"21{i:08d}"
        nama = f"Mahasiswa-{i}"
        prodi = random.choice(PRODI)
        angkatan = random.choice([2021,2022,2023])
        daftar.append(Mahasiswa(nim, nama, prodi, angkatan))
    return daftar

# ====================== ANALISIS PERFORMA ======================
def ukur_waktu(f, *args) -> float:
    mulai = time.perf_counter()
    hasil = f(*args)
    selesai = time.perf_counter()
    return selesai - mulai

# ====================== ANTARMUKA CLI ======================
def main():
    bst = BSTMahasiswa()
    undo_stack = Stack()
    graph_prereq = GraphPrereq()

    # Inisialisasi data matkul contoh
    kode_mk_list = [f"ELT{i:03d}" for i in range(1,41)]
    for kode in kode_mk_list:
        graph_prereq.tambah_matkul(kode, f"Mata Kuliah {kode}")
    # tambah contoh prasyarat
    for i in range(2,41):
        graph_prereq.tambah_prasyarat(kode_mk_list[i-1], kode_mk_list[i-2])

    # Masukkan mahasiswa
    for mhs in generate_mahasiswa(60):
        bst.insert(mhs)

    print("=== AKADEMIK PERFORMANCE TRACKER ===")
    print("Perintah: CARI_MHS <nim>, INPUT_NILAI <nim> <kode> <sks> <nilai> <sem>, UNDO_NILAI <nim>,")
    print("TRANSKRIPSI <nim>, IPK <nim>, RANKING_IPK, FILTER_IPK <min> <max>, PRASYARAT_CEK <nim> <kode>, URUTAN_MATKUL, KELUAR")

    while True:
        cmd = input(">> ").strip().split()
        if not cmd: continue
        if cmd[0].upper() == "KELUAR": break

        elif cmd[0].upper() == "CARI_MHS":
            node = bst.search(cmd[1])
            if node: print(f"NIM: {node.mhs.nim}, Nama: {node.mhs.nama}, IPK: {node.mhs.ipk}")
            else: print("Tidak ditemukan")

        elif cmd[0].upper() == "INPUT_NILAI":
            nim,kode,sks,gr,sem = cmd[1],cmd[2],int(cmd[3]),cmd[4],int(cmd[5])
            node = bst.search(nim)
            if node:
                n = NilaiMatkul(kode, graph_prereq.nama_mk.get(kode,"-"), sks, gr, sem)
                node.transkrip.tambah_nilai(n)
                undo_stack.push( ("HAPUS", nim, n) )
                bst.update_ipk(nim)
                print("Nilai dimasukkan")
            else: print("Mahasiswa tidak ada")

        elif cmd[0].upper() == "UNDO_NILAI":
            if undo_stack.is_empty(): print("Tidak ada yang di-undo")
            else:
                aksi, nim, n = undo_stack.pop()
                node = bst.search(nim)
                if aksi == "HAPUS" and node:
                    terhapus = node.transkrip.hapus_terakhir()
                    bst.update_ipk(nim)
                    print(f"Dihapus: {terhapus}")

        elif cmd[0].upper() == "TRANSKRIPSI":
            node = bst.search(cmd[1])
            if node:
                curr = node.transkrip.head
                while curr:
                    print(curr.data)
                    curr = curr.next

        elif cmd[0].upper() == "IPK":
            node = bst.search(cmd[1])
            if node: print(f"IPK: {node.mhs.ipk}")

        elif cmd[0].upper() == "RANKING_IPK":
            daftar = bst.inorder()
            # buat linked list untuk sorting
            head = None
            for m in daftar:
                nd = DLLNode(m)
                nd.next = head
                if head: head.prev = nd
                head = nd
            urut = merge_sort_ll(head)
            curr = urut
            i=1
            while curr:
                print(f"{i}. {curr.data.nama}-{curr.data.nim}: {curr.data.ipk}")
                curr = curr.next
                i += 1

        elif cmd[0].upper() == "FILTER_IPK":
            low,high = float(cmd[1]),float(cmd[2])
            hasil = bst.range_ipk(low,high)
            for h in hasil: print(f"{h.nama}: {h.ipk}")

        elif cmd[0].upper() == "PRASYARAT_CEK":
            node = bst.search(cmd[1])
            if node and graph_prereq.prasyarat_terpenuhi(node, cmd[2]):
                print("Bisa ambil matkul ini")
            else: print("Belum memenuhi prasyarat")

        elif cmd[0].upper() == "URUTAN_MATKUL":
            urutan = graph_prereq.topological_sort()
            print([graph_prereq.nama_mk[k] for k in urutan])

if __name__ == "__main__":
    main()
