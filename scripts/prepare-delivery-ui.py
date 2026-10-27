from pathlib import Path
import re


def replace_style_delivery_fee(text):
    start = text.find('function styleDeliveryFee(p,quantity=1){')
    if start < 0:
        return text
    brace = text.find('{', start)
    depth = 0
    end = None
    for i in range(brace, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        return text
    fn = ('function styleDeliveryFee(p,quantity=1){if(p&&p.freeDelivery!==true)return 0;'
          'const q=Math.max(1,Number(quantity)||1);'
          'if(p&&Array.isArray(p.deliveryRanges)&&p.deliveryRanges.length){'
          'const r=p.deliveryRanges.find(x=>q>=Number(x.min)&&q<=Number(x.max));'
          'if(r)return Math.max(0,Number(r.fee)||0);'
          'const last=[...p.deliveryRanges].sort((a,b)=>Number(a.min)-Number(b.min)).slice(-1)[0];'
          'if(last&&q>Number(last.max))return Math.max(0,Number(last.fee)||0)}'
          'if(p&&p.deliveryFee!==null&&p.deliveryFee!==undefined&&p.deliveryFee!=="")return Math.max(0,Number(p.deliveryFee)||0);'
          'return 0}')
    return text[:start] + fn + text[end:]


# Admin panel: one switch only. When OFF, no delivery fee is applied and no FREE label is shown.
p = Path('admin.html')
s = p.read_text(encoding='utf-8')
start = s.find('<div class="full" style="background:#fff0f6;border:2px solid #7b284f')
end = s.find('<div><label>කාණ්ඩය *', start)
if start >= 0 and end >= 0:
    section = '''<div class="full" style="background:#fff0f6;border:2px solid #7b284f;border-radius:12px;padding:12px"><h3 style="color:#7b284f;margin:0 0 6px">🚚 Delivery</h3><p class="small">ඇඳුමේ සාමාන්‍ය මිල ඉහළින් දාන්න. “FREE DELIVERY” tick කළොත් මේ Style එකේ වෙබ් අඩවියේ Delivery Free ලෙස පෙන්වයි. පහළ Quantity Ranges මගින් ඇතුළත Delivery ගණනය සකසන්න.</p><label style="display:flex;gap:8px;align-items:flex-start;margin:10px 0"><input id="freeDelivery" type="checkbox" style="width:auto;margin-top:4px"><span><strong>FREE DELIVERY</strong><br><span class="small">Tick කළොත් “DELIVERY FREE” පෙන්වයි සහ Delivery setting සක්‍රීය වේ. Tick නොකළොත් Delivery fee එකක් එකතු නොවන අතර “DELIVERY FREE” පෙන්වන්නේ නැහැ.</span></span></label><div id="productDeliveryFields" hidden><label for="productBaseDeliveryFee">Delivery ගාස්තුව (රු.)</label><input id="productBaseDeliveryFee" type="number" min="0" step="0.01" placeholder="උදා: 100"><p class="small">Quantity අනුව වෙනස් කිරීමට ranges දාන්න. උදා: 1–3 = රු.100, 4–4 = රු.200.</p><div id="productDeliveryRangeRows" style="display:grid;gap:10px;margin:12px 0"></div><div style="display:flex;gap:8px;flex-wrap:wrap"><button type="button" class="secondary" id="addProductDeliveryRange">＋ Quantity Range එකක් එක් කරන්න</button><button type="button" class="secondary" id="resetProductDeliveryRanges">Quantity Ranges ඉවත් කරන්න</button></div><p id="productDeliveryMessage" class="small"></p></div></div>'''
    s = s[:start] + section + s[end:]

s = s.replace('productDeliveryEnabled', 'freeDelivery')
s = re.sub(r'\$\("allowCOD"\)\.checked\s*=\s*[^;]+;?', '', s)
s = re.sub(r'allowCOD:\$\("allowCOD"\)\.checked,?', '', s)
s = re.sub(r'\$\("hideDeliveryForNonCOD"\)\.checked\s*=\s*[^;]+;?', '', s)
s = re.sub(r'hideDeliveryForNonCOD:\$\("hideDeliveryForNonCOD"\)\.checked,?', '', s)
s = s.replace('freeDelivery:$(' + '"freeDelivery"' + ').checked,deliveryFee:', 'freeDelivery:$(' + '"freeDelivery"' + ').checked,deliveryFeeEnabled:$(' + '"freeDelivery"' + ').checked,deliveryFee:')
s = re.sub(r'\$\("freeDelivery"\)\.checked\s*=\s*p\.deliveryFeeEnabled===true[^;]*;', '$("freeDelivery").checked=p.freeDelivery===true||p.deliveryFeeEnabled===true;', s)
if '$("freeDelivery").addEventListener("change"' not in s:
    marker = 'function defaultProductDeliveryRanges(){return[]}'
    if marker in s:
        s = s.replace(marker, '$("freeDelivery").addEventListener("change",()=>{$("productDeliveryFields").hidden=!$("freeDelivery").checked});\n' + marker, 1)
p.write_text(s, encoding='utf-8')

# Main page: only the Free Delivery flag enables delivery calculation and badge.
p = Path('index.html')
s = replace_style_delivery_fee(p.read_text(encoding='utf-8'))
needle = 'const cs=colours(p.colors),badges=document.createElement("div");'
if needle in s and 'p.freeDelivery===true){const fd=' not in s:
    s = s.replace(needle, 'const cs=colours(p.colors),badges=document.createElement("div");if(p.freeDelivery===true){const fd=document.createElement("span");fd.className="badge";fd.style.cssText="background:#d8fbe4;color:#075d2c;border:2px solid #21a45b;font-weight:900";fd.textContent="🚚 DELIVERY FREE";badges.appendChild(fd)}', 1)
s = s.replace('deliveryFeeEnabled:x.deliveryFeeEnabled===true,allowCOD:x.allowCOD!==false,styleNumber:', 'freeDelivery:x.freeDelivery===true,deliveryFeeEnabled:x.freeDelivery===true,styleNumber:')
s = s.replace('deliveryFeeEnabled:x.deliveryFeeEnabled===true,styleNumber:', 'freeDelivery:x.freeDelivery===true,deliveryFeeEnabled:x.freeDelivery===true,styleNumber:')
p.write_text(s, encoding='utf-8')

# Product page: same switch; show the existing prominent FREE badge only when enabled.
p = Path('product.html')
s = replace_style_delivery_fee(p.read_text(encoding='utf-8'))
s = s.replace('deliveryFeeEnabled:p.deliveryFeeEnabled===true,allowCOD:p.allowCOD!==false,deliveryFee:', 'freeDelivery:p.freeDelivery===true,deliveryFeeEnabled:p.freeDelivery===true,deliveryFee:')
s = s.replace('deliveryFeeEnabled:p.deliveryFeeEnabled===true,deliveryFee:', 'freeDelivery:p.freeDelivery===true,deliveryFeeEnabled:p.freeDelivery===true,deliveryFee:')
# Remove the separate delivery-fee text from the customer-facing product page; the FREE badge is the only label.
s = s.replace('if(paymentSelect.value==="COD"&&p.deliveryFeeEnabled===true){const feeNote=node("div","Delivery ගාස්තුව (customer ගෙවිය යුතුයි): රු. "+fee.toLocaleString("en-LK"),"muted");feeNote.style.marginTop="6px";priceBox.appendChild(feeNote);}', 'if(p.freeDelivery===true){const feeNote=node("div","🚚 DELIVERY FREE","free-delivery-badge");priceBox.appendChild(feeNote);}')
p.write_text(s, encoding='utf-8')
