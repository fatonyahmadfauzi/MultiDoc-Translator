#!/usr/bin/env python3
"""
DISPLAY LANGUAGES TOOL
Alat lengkap untuk memeriksa konsistensi dan mengelola section DISPLAY_LANGUAGES di file Python
"""

import os
import re
import ast
import sys
import argparse
from pathlib import Path

# ==================== FUNGSI CHECKER (ANALISIS) ====================

def find_display_languages_files(directory="."):
    """
    Mencari file Python yang mengandung DISPLAY_LANGUAGES secara otomatis
    """
    python_files = []
    display_languages_files = []
    
    print("🔍 MENCARI FILE PYTHON YANG MENGANDUNG DISPLAY_LANGUAGES...")
    print("=" * 60)
    
    # Cari semua file .py di direktori dan subdirektori
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                python_files.append(full_path)
    
    print(f"📁 Ditemukan {len(python_files)} file Python")
    
    # Periksa setiap file Python untuk DISPLAY_LANGUAGES
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Cek dengan regex untuk DISPLAY_LANGUAGES
            if re.search(r'DISPLAY_LANGUAGES\s*=', content):
                display_languages_files.append(file_path)
                print(f"✅ Ditemukan di: {file_path}")
                
        except Exception as e:
            print(f"⚠️  Gagal membaca {file_path}: {e}")
    
    print(f"\n📊 Total file dengan DISPLAY_LANGUAGES: {len(display_languages_files)}")
    return display_languages_files

def extract_display_languages_from_file(file_path):
    """
    Mengekstrak dictionary DISPLAY_LANGUAGES dari file Python
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip file ini sendiri untuk menghindari circular reference
        if os.path.basename(file_path) == 'display_languages_tool.py':
            return None
        
        # Method 1: Menggunakan AST untuk parsing yang aman
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == 'DISPLAY_LANGUAGES':
                            # Ekstrak dictionary menggunakan exec
                            local_vars = {}
                            global_vars = {}
                            exec(content, global_vars, local_vars)
                            
                            # Cari DISPLAY_LANGUAGES di local_vars atau global_vars
                            if 'DISPLAY_LANGUAGES' in local_vars:
                                result = local_vars['DISPLAY_LANGUAGES']
                            elif 'DISPLAY_LANGUAGES' in global_vars:
                                result = global_vars['DISPLAY_LANGUAGES']
                            else:
                                return None
                            
                            # Validasi bahwa hasilnya adalah dictionary
                            if isinstance(result, dict) and result:
                                return result
        except Exception as e:
            if '--verbose' in sys.argv:
                print(f"⚠️  AST parsing failed for {file_path}: {e}")
        
        # Method 2: Menggunakan regex untuk ekstraksi manual
        # Mencari pattern DISPLAY_LANGUAGES = { ... }
        pattern = r'DISPLAY_LANGUAGES\s*=\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(pattern, content, re.DOTALL)
        
        if matches:
            # Ambil match terpanjang (yang paling lengkap)
            longest_match = max(matches, key=len)
            try:
                # Evaluasi string menjadi dictionary
                display_languages = eval(longest_match.split('=', 1)[1].strip())
                if isinstance(display_languages, dict) and display_languages:
                    return display_languages
            except Exception as e:
                if '--verbose' in sys.argv:
                    print(f"⚠️  Regex extraction failed for {file_path}: {e}")
        
        return None
        
    except Exception as e:
        if '--verbose' in sys.argv:
            print(f"❌ Gagal mengekstrak dari {file_path}: {e}")
        return None

def analyze_display_languages(file_path, display_languages):
    """
    Menganalisis konsistensi DISPLAY_LANGUAGES dari file
    """
    print(f"\n📊 ANALISIS: {os.path.basename(file_path)}")
    print("=" * 60)
    
    if not display_languages:
        print("❌ DISPLAY_LANGUAGES tidak valid atau tidak dapat diekstrak")
        return None
    
    # Validasi tipe data
    if not isinstance(display_languages, dict):
        print(f"❌ DISPLAY_LANGUAGES bukan dictionary, tipe: {type(display_languages)}")
        return None
    
    # Ambil bahasa pertama sebagai referensi
    available_langs = list(display_languages.keys())
    if not available_langs:
        print("❌ Tidak ada bahasa yang ditemukan")
        return None
    
    # Validasi struktur nested dictionary
    reference_lang = available_langs[0]
    if not isinstance(display_languages[reference_lang], dict):
        print(f"❌ Struktur tidak valid untuk bahasa {reference_lang}")
        return None
    
    reference_phrases = set(display_languages[reference_lang].keys())
    
    print(f"🌐 Bahasa referensi: {reference_lang.upper()} ({len(reference_phrases)} phrases)")
    print(f"📝 Total bahasa: {len(available_langs)}")
    
    # 1. Periksa jumlah phrases per bahasa
    print(f"\n📈 JUMLAH PHRASES PER BAHASA:")
    print("-" * 35)
    
    inconsistent_langs = {}
    valid_langs = []
    
    for lang_code in available_langs:
        # Validasi setiap bahasa
        if not isinstance(display_languages[lang_code], dict):
            print(f"❌ {lang_code.upper()}: Bukan dictionary, dilompati")
            continue
            
        count = len(display_languages[lang_code])
        expected = len(reference_phrases)
        status = "✅" if count == expected else "❌"
        print(f"{status} {lang_code.upper()}: {count} phrases")
        
        valid_langs.append(lang_code)
        if count != expected:
            inconsistent_langs[lang_code] = count
    
    if not valid_langs:
        print("❌ Tidak ada bahasa yang valid untuk dianalisis")
        return None
    
    # 2. Periksa phrases yang hilang
    print(f"\n🔎 PHRASES YANG HILANG:")
    print("-" * 25)
    
    all_missing = {}
    for lang_code in valid_langs:
        if lang_code == reference_lang:
            continue
            
        current_phrases = set(display_languages[lang_code].keys())
        missing_phrases = reference_phrases - current_phrases
        
        if missing_phrases:
            all_missing[lang_code] = missing_phrases
            print(f"\n❌ {lang_code.upper()} - {len(missing_phrases)} phrases hilang:")
            for phrase in sorted(list(missing_phrases))[:5]:  # Tampilkan 5 pertama
                print(f"   - {phrase}")
            if len(missing_phrases) > 5:
                print(f"   ... dan {len(missing_phrases) - 5} lainnya")
    
    if not all_missing:
        print("✅ Tidak ada phrases yang hilang")
    
    # 3. Deteksi duplikat
    print(f"\n🔍 DETEKSI DUPLIKAT:")
    print("-" * 20)
    
    has_duplicates = False
    for lang_code in valid_langs:
        phrases = list(display_languages[lang_code].keys())
        if len(phrases) != len(set(phrases)):
            has_duplicates = True
            print(f"❌ {lang_code.upper()}: Ada duplikat phrases")
            
            # Tampilkan duplikatnya
            seen = set()
            duplicates = set()
            for phrase in phrases:
                if phrase in seen:
                    duplicates.add(phrase)
                else:
                    seen.add(phrase)
            
            if duplicates:
                print(f"   Duplikat: {', '.join(sorted(duplicates))}")
        else:
            print(f"✅ {lang_code.upper()}: Tidak ada duplikat")
    
    # 4. Ringkasan
    print(f"\n📋 RINGKASAN UNTUK {os.path.basename(file_path)}:")
    print("-" * 40)
    print(f"✅ Bahasa konsisten: {len(valid_langs) - len(inconsistent_langs)}/{len(valid_langs)}")
    print(f"❌ Bahasa tidak konsisten: {len(inconsistent_langs)}")
    print(f"📝 Phrases referensi: {len(reference_phrases)}")
    print(f"🔍 Duplikat ditemukan: {'Ya' if has_duplicates else 'Tidak'}")
    
    # 5. Tampilkan beberapa phrases contoh
    if reference_phrases:
        print(f"\n🔤 CONTOH PHRASES ({min(5, len(reference_phrases))} pertama):")
        print("-" * 30)
        for phrase in sorted(list(reference_phrases))[:5]:
            print(f"   - {phrase}")
    
    return {
        'file_path': file_path,
        'total_languages': len(valid_langs),
        'reference_phrases_count': len(reference_phrases),
        'inconsistent_langs': inconsistent_langs,
        'missing_phrases': all_missing,
        'has_duplicates': has_duplicates,
        'reference_lang': reference_lang
    }

def quick_check(file_path):
    """
    Pengecekan cepat untuk file tertentu
    """
    print(f"🔍 QUICK CHECK: {os.path.basename(file_path)}")
    display_languages = extract_display_languages_from_file(file_path)
    
    if display_languages:
        return analyze_display_languages(file_path, display_languages)
    else:
        print("❌ Gagal mengekstrak DISPLAY_LANGUAGES")
        return None

def check_current_directory():
    """
    Pengecekan otomatis di direktori saat ini
    """
    files = find_display_languages_files()
    results = []
    
    for file_path in files:
        print(f"\n{'='*60}")
        display_languages = extract_display_languages_from_file(file_path)
        if display_languages:
            result = analyze_display_languages(file_path, display_languages)
            if result:
                results.append(result)
        else:
            print(f"⏭️  Lewati {os.path.basename(file_path)}: tidak dapat diekstrak")
    
    # Tampilkan ringkasan akhir
    if results:
        print("\n" + "=" * 60)
        print("🎯 RINGKASAN AKHIR SEMUA FILE:")
        print("=" * 60)
        for result in results:
            filename = os.path.basename(result['file_path'])
            consistent = result['total_languages'] - len(result['inconsistent_langs'])
            status = "❌" if result['inconsistent_langs'] or result['has_duplicates'] else "✅"
            print(f"{status} {filename}: {consistent}/{result['total_languages']} bahasa konsisten, {result['reference_phrases_count']} phrases")
    else:
        print("\n❌ Tidak ada file yang berhasil dianalisis")
    
    return results

# ==================== FUNGSI MANAGER (KELOLA SECTION) ====================

def create_display_languages_section(file_path, languages=None):
    """
    Membuat section DISPLAY_LANGUAGES baru di file Python
    """
    try:
        # Bahasa default jika tidak ditentukan
        if languages is None:
            languages = ['en', 'id', 'jp', 'de', 'es', 'fr', 'kr', 'pl', 'pt', 'ru', 'zh']
        
        # Baca konten file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Cek apakah section sudah ada
        if re.search(r'# -+ DISPLAY LANGUAGE SETTINGS -+', content):
            print(f"❌ Section DISPLAY_LANGUAGES sudah ada di {file_path}")
            return False
        
        # Buat template DISPLAY_LANGUAGES
        display_languages_template = f'''# ---------------------- DISPLAY LANGUAGE SETTINGS ----------------------
DISPLAY_LANGUAGES = {{
    "en": {{
        # English translations will go here
    }}'''
        
        # Tambahkan bahasa lainnya
        for lang in languages[1:]:  # Skip 'en' karena sudah ditambahkan
            display_languages_template += f''',
    "{lang}": {{
        # {lang.upper()} translations will go here
    }}'''
        
        display_languages_template += '\n}'
        
        # Cari tempat yang tepat untuk menambahkan section
        # Biasanya di bagian atas file setelah imports
        lines = content.split('\n')
        insert_position = 0
        
        # Cari setelah imports dan module docstring
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith(('#', 'import', 'from', '"', "'")):
                insert_position = i
                break
        else:
            insert_position = len(lines)
        
        # Sisipkan section
        lines.insert(insert_position, '')
        lines.insert(insert_position, display_languages_template)
        lines.insert(insert_position, '')
        
        # Tulis kembali file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Berhasil membuat section DISPLAY_LANGUAGES di {file_path}")
        print(f"🌐 Bahasa yang ditambahkan: {', '.join(languages)}")
        return True
        
    except Exception as e:
        print(f"❌ Gagal membuat section di {file_path}: {e}")
        return False

def remove_display_languages_section(file_path):
    """
    Menghapus section DISPLAY_LANGUAGES dari file Python
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern untuk menemukan section DISPLAY_LANGUAGES
        pattern = r'# -+ DISPLAY LANGUAGE SETTINGS -+.*?^DISPLAY_LANGUAGES\s*=\s*\{.*?\n\}'
        match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
        
        if not match:
            print(f"❌ Section DISPLAY_LANGUAGES tidak ditemukan di {file_path}")
            return False
        
        # Hapus section
        new_content = content[:match.start()] + content[match.end():]
        
        # Hapus baris kosong berlebihan
        new_content = re.sub(r'\n\s*\n\s*\n', '\n\n', new_content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Berhasil menghapus section DISPLAY_LANGUAGES dari {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Gagal menghapus section dari {file_path}: {e}")
        return False

def create_empty_display_languages(languages=None):
    """
    Membuat template DISPLAY_LANGUAGES kosong untuk copy-paste
    """
    if languages is None:
        languages = ['en', 'id', 'jp', 'de', 'es', 'fr', 'kr', 'pl', 'pt', 'ru', 'zh']
    
    template = '''# ---------------------- DISPLAY LANGUAGE SETTINGS ----------------------
DISPLAY_LANGUAGES = {'''
    
    for i, lang in enumerate(languages):
        if i == 0:
            template += f'''
    "{lang}": {{
        # {lang.upper()} translations will go here
    }}'''
        else:
            template += f''',
    "{lang}": {{
        # {lang.upper()} translations will go here
    }}'''
    
    template += '\n}'
    
    print("📋 TEMPLATE DISPLAY_LANGUAGES KOSONG:")
    print("=" * 50)
    print(template)
    print("=" * 50)
    
    return template

def list_files_with_display_languages(directory="."):
    """
    Menampilkan file yang sudah memiliki section DISPLAY_LANGUAGES
    """
    python_files = []
    
    print("🔍 MENCARI FILE DENGAN DISPLAY_LANGUAGES...")
    print("=" * 50)
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if re.search(r'DISPLAY_LANGUAGES\s*=', content):
                        python_files.append(full_path)
                        print(f"✅ {full_path}")
                        
                except Exception as e:
                    print(f"⚠️  Gagal membaca {full_path}: {e}")
    
    print(f"\n📊 Total file dengan DISPLAY_LANGUAGES: {len(python_files)}")
    return python_files

# ==================== FUNGSI UTAMA & INTERFACE ====================

def interactive_mode():
    """
    Mode interaktif untuk pengguna
    """
    print("🚀 DISPLAY LANGUAGES TOOL")
    print("=" * 35)
    print("1. 🔍 Check Consistency (Analisis)")
    print("2. 🛠️  Manage Sections (Kelola)")
    print("3. 📋 Create Template (Buat Template)")
    print("4. 📊 List Files (Daftar File)")
    
    choice = input("\nPilihan (1-4): ").strip()
    
    if choice == '1':
        # Mode analisis
        print("\n🎯 CHECK CONSISTENCY")
        files = find_display_languages_files()
        if not files:
            print("❌ Tidak ditemukan file dengan DISPLAY_LANGUAGES")
            return
        
        analyzable_files = []
        for file_path in files:
            if extract_display_languages_from_file(file_path):
                analyzable_files.append(file_path)
        
        if not analyzable_files:
            print("❌ Tidak ada file yang dapat dianalisis")
            return
        
        print(f"\n📁 Ditemukan {len(analyzable_files)} file yang dapat dianalisis:")
        for i, file_path in enumerate(analyzable_files, 1):
            print(f"{i}. {os.path.basename(file_path)}")
        
        file_choice = input(f"\nPilih file (1-{len(analyzable_files)}) atau Enter untuk semua: ").strip()
        
        if file_choice.isdigit() and 1 <= int(file_choice) <= len(analyzable_files):
            quick_check(analyzable_files[int(file_choice) - 1])
        else:
            check_current_directory()
    
    elif choice == '2':
        # Mode kelola section
        print("\n🛠️  MANAGE SECTIONS")
        print("1. Buat section baru")
        print("2. Hapus section")
        
        sub_choice = input("\nPilihan (1-2): ").strip()
        
        if sub_choice == '1':
            file_path = input("Masukkan path file Python: ").strip()
            if os.path.exists(file_path):
                langs_input = input("Bahasa (kosong untuk default): ").strip()
                languages = [lang.strip() for lang in langs_input.split(',')] if langs_input else None
                create_display_languages_section(file_path, languages)
            else:
                print("❌ File tidak ditemukan")
        
        elif sub_choice == '2':
            file_path = input("Masukkan path file Python: ").strip()
            if os.path.exists(file_path):
                remove_display_languages_section(file_path)
            else:
                print("❌ File tidak ditemukan")
    
    elif choice == '3':
        # Buat template
        print("\n📋 CREATE TEMPLATE")
        langs_input = input("Bahasa (kosong untuk default): ").strip()
        languages = [lang.strip() for lang in langs_input.split(',')] if langs_input else None
        create_empty_display_languages(languages)
    
    elif choice == '4':
        # List files
        print("\n📊 LIST FILES")
        list_files_with_display_languages()
    
    else:
        print("❌ Pilihan tidak valid")

def setup_argparse():
    parser = argparse.ArgumentParser(
        description='DISPLAY LANGUAGES TOOL - Alat lengkap untuk analisis dan manajemen DISPLAY_LANGUAGES',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
CONTOH PENGGUNAAN:

  🎯 ANALISIS (CHECK):
    python display_languages_tool.py check --auto
    python display_languages_tool.py check multidoc_translator.py
    python display_languages_tool.py check --interactive

  🛠️  KELOLA (MANAGE):
    python display_languages_tool.py create my_script.py
    python display_languages_tool.py create my_script.py --langs en,id,jp
    python display_languages_tool.py remove my_script.py

  📋 UTILITAS:
    python display_languages_tool.py template
    python display_languages_tool.py template --langs en,es,fr
    python display_languages_tool.py list
    python display_languages_tool.py --interactive
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Parser untuk CHECK
    check_parser = subparsers.add_parser('check', help='Check consistency of DISPLAY_LANGUAGES')
    check_parser.add_argument('file', nargs='?', help='Specific Python file to check')
    check_parser.add_argument('-a', '--auto', action='store_true', help='Auto-detect files')
    check_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    check_parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    
    # Parser untuk CREATE
    create_parser = subparsers.add_parser('create', help='Create DISPLAY_LANGUAGES section')
    create_parser.add_argument('file', help='Python file to modify')
    create_parser.add_argument('--langs', help='Comma-separated language codes')
    
    # Parser untuk REMOVE
    remove_parser = subparsers.add_parser('remove', help='Remove DISPLAY_LANGUAGES section')
    remove_parser.add_argument('file', help='Python file to modify')
    
    # Parser untuk TEMPLATE
    template_parser = subparsers.add_parser('template', help='Create empty template')
    template_parser.add_argument('--langs', help='Comma-separated language codes')
    
    # Parser untuk LIST
    list_parser = subparsers.add_parser('list', help='List files with DISPLAY_LANGUAGES')
    list_parser.add_argument('--dir', default='.', help='Directory to search')
    
    # Global options
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    
    return parser

def main():
    """
    Fungsi utama
    """
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Mode interaktif
    if args.interactive or (not args.command and len(sys.argv) == 1):
        interactive_mode()
        return
    
    if args.command == 'check':
        if args.file:
            quick_check(args.file)
        elif args.auto:
            check_current_directory()
        elif args.interactive:
            interactive_mode()
        else:
            print("❌ Gunakan --auto atau tentukan file")
    
    elif args.command == 'create':
        if not os.path.exists(args.file):
            print(f"❌ File tidak ditemukan: {args.file}")
            return
        
        languages = None
        if args.langs:
            languages = [lang.strip() for lang in args.langs.split(',')]
        
        create_display_languages_section(args.file, languages)
    
    elif args.command == 'remove':
        if not os.path.exists(args.file):
            print(f"❌ File tidak ditemukan: {args.file}")
            return
        
        remove_display_languages_section(args.file)
    
    elif args.command == 'template':
        languages = None
        if args.langs:
            languages = [lang.strip() for lang in args.langs.split(',')]
        
        create_empty_display_languages(languages)
    
    elif args.command == 'list':
        list_files_with_display_languages(args.dir)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()