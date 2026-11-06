# 1. ORCID resolves
curl -sI https://orcid.org/0009-0005-4309-7476 | head -1
# → HTTP/2 200

# 2. Repo public
gh repo view thanu2008v-prog/senthamil-marabu --json visibility -q .visibility
# → PUBLIC

# 3. Latest CI run
gh run list -R thanu2008v-prog/senthamil-marabu --limit 1
# → ✓ build-nool  main  ...

# 4. Single-file SHA (மூலம் intact — poruḷ 652)
python3 scripts/build_single_file.py --sha
# → SHA-256 (mūlam, NFC): <hex>
#   Records: 1602 / Othu: 27 / Padalam: 3

# 5. All 1602 rendered
python3 scripts/build_single_file.py --dry
# → Sutras: 1602  Othu: 27  Padalam: 3