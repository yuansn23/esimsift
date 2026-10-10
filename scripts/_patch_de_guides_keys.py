#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 i18n/de.toml 里仍为英文的 guides_region / guides_single key 译成德语。

纪律：
  * bytes 读写（读 bytes -> 解码 -> 逐行改 -> 编码 -> 写 bytes），复核 LF 行尾未被破坏
  * **断言旧值等于 en.toml 的对应值** —— 只允许改「尚未翻译」的 key，防止覆盖已有译文
  * 幂等：值已是目标德语时跳过
  * --dry 只报告
"""
import pathlib
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DE = ROOT / 'i18n' / 'de.toml'
EN = ROOT / 'i18n' / 'en.toml'

# key 后缀 -> 德语译文（键名全写，避免歧义）
T = {
    # ── guides_region（区域指南模板标签） ──
    'guides_region__cheapest_entry_plan': 'Günstigster Einstiegstarif',
    'guides_region__cheapest_in_the_most_countries': 'In den meisten Ländern am günstigsten',
    'guides_region__countries_tracked': 'Erfasste Länder',
    'guides_region__countries_where_it_is_cheapest': 'Länder, in denen er am günstigsten ist',
    'guides_region__esim_brands_compared': 'Verglichene eSIM-Marken',
    'guides_region__explore': 'Entdecken',
    'guides_region__one_destination': 'Ein Reiseziel',
    'guides_region__prices_checked': 'Preise geprüft',
    'guides_region__region_guide': 'Regionaler Ratgeber',
    'guides_region__regional_average_gb': 'Regionaler Durchschnitt $/GB',
    'guides_region__regional_average_gb_2': 'Regionaler Durchschnitt $/GB',
    'guides_region__several_destinations': 'Mehrere Reiseziele',
    'guides_region__the_numbers': 'Die Zahlen',
    'guides_region__the_verdict': 'Das Fazit',
    'guides_region__unlimited_plans': 'Unlimited-Tarife',
    # ── guides_single（教程页模板标签） ──
    'guides_single__app_required': 'App erforderlich',
    'guides_single__brand': 'Marke',
    'guides_single__buy_on_the_website_scan_the_qr_code_or_approve_the_web_i':
        'Kauf auf der Website, QR-Code scannen (oder die Web-Installation bestätigen) '
        '— keine zusätzliche App und kein Konto nötig.',
    'guides_single__compare_esims_by_country': 'eSIMs nach Land vergleichen',
    'guides_single__compatibility_traps_cluster_around_phones_that_look_fine':
        'Kompatibilitätsfallen sammeln sich bei Geräten, die auf dem Papier einwandfrei aussehen. '
        'Die meisten dieser Modelle tragen denselben Namen und dasselbe Modelljahr wie eine '
        'eSIM-fähige Version — doch die konkret in diesem Markt verkaufte Variante hat den Chip '
        'nicht. Wenn Händler und Datenblatt sich widersprechen, entscheidet der EID-Test.',
    'guides_single__direct_install': 'Direktinstallation',
    'guides_single__eid_test_in_the_guide_above_is_always_the_final_word':
        'Der EID-Test im Ratgeber oben gibt immer den Ausschlag.',
    'guides_single__estimate_your_data_by_app_then_get_the_cheapest_real_pla':
        'Schätze deinen Datenbedarf pro App und hole dir dann den günstigsten echten Tarif '
        'für deine Reisedaten.',
    'guides_single__every_model_we_could_verify': 'Jedes Modell, das wir prüfen konnten —',
    'guides_single__how_each_provider_installs_its_esim':
        'Wie jeder Anbieter seine eSIM installiert',
    'guides_single__install_method': 'Installationsweg',
    'guides_single__last_reviewed': 'Zuletzt geprüft',
    'guides_single__live_device_database': 'Live-Gerätedatenbank',
    'guides_single__model_or_variant': 'Modell oder Variante',
    'guides_single__no_models_match_that_search_a_miss_here_is_not_a_verdict':
        'Keine Modelle zu dieser Suche. Ein Trefferausfall ist kein Urteil — viele regionale '
        'Varianten schaffen es in keine veröffentlichte Liste. Wähle',
    'guides_single__on_the_phone_itself_an_eid_number_on_screen_means_the_es':
        'am Telefon selbst: eine EID-Nummer auf dem Bildschirm bedeutet, dass der eSIM-Chip '
        'vorhanden ist.',
    'guides_single__provider_app': 'Anbieter-App',
    'guides_single__reading_time': 'Lesezeit',
    'guides_single__search_a_model_try_iphone_15_s24_or_pixel':
        'Modell suchen — z. B. iPhone 15, S24 oder Pixel',
    'guides_single__search_devices': 'Geräte suchen',
    'guides_single__the_app_handles_purchase_and_install_in_one_place_instal':
        'Die App erledigt Kauf und Installation an einer Stelle — installiere sie noch zu Hause '
        'im WLAN, bevor du fliegst.',
    'guides_single__variant_watch': 'Varianten-Warnung:',
    'guides_single__what_it_means_at_install_time': 'Was das bei der Installation bedeutet',
    'guides_single__which_esim_providers_require_their_app':
        'Welche eSIM-Anbieter setzen ihre App voraus',
    'guides_single__which_phones_and_tablets_support_esim':
        'Welche Smartphones und Tablets unterstützen eSIM?',
    'guides_single__which_popular_phones_do_not_support_esim':
        'Welche beliebten Smartphones unterstützen eSIM nicht?',
    'guides_single__why_it_fails': 'Warum es scheitert',
}


def flat(d, p=''):
    for k, v in d.items():
        if isinstance(v, dict):
            yield from flat(v, p + k + '.')
        else:
            yield p + k, v


def esc(v):
    return v.replace('\\', '\\\\').replace('"', '\\"')


def main():
    dry = '--dry' in sys.argv
    E = dict(flat(tomllib.load(open(EN, 'rb'))))
    raw = DE.read_bytes()
    text = raw.decode('utf-8')
    assert raw.count(b'\r\n') == 0, 'de.toml 出现 CRLF'
    lines = text.split('\n')

    idx = {}
    for i, ln in enumerate(lines):
        if ' = "' in ln and not ln.lstrip().startswith('#'):
            idx[ln.split(' = ', 1)[0].strip()] = i

    done = skip = fail = 0
    for key, de_val in T.items():
        assert key in E, f'{key} 不在 en.toml'
        i = idx.get(key)
        if i is None:
            print(f'  !! 找不到行: {key}')
            fail += 1
            continue
        cur = lines[i].split(' = ', 1)[1]
        cur_val = cur[1:-1].replace('\\"', '"').replace('\\\\', '\\') if cur.startswith('"') else None
        if cur_val == de_val:
            skip += 1
            continue
        if cur_val != E[key]:
            print(f'  !! 旧值既非英文也非目标德语，拒绝覆盖: {key}\n      现值={cur_val!r}')
            fail += 1
            continue
        lines[i] = f'{key} = "{esc(de_val)}"'
        done += 1

    print(f'译 {done} / 已是目标值跳过 {skip} / 失败 {fail}（共 {len(T)}）')
    if fail or dry:
        return 1 if fail else 0

    out = '\n'.join(lines).encode('utf-8')
    DE.write_bytes(out)
    chk = DE.read_bytes()
    assert chk.count(b'\r\n') == 0, '写回后出现 CRLF'
    D = dict(flat(tomllib.load(open(DE, 'rb'))))
    assert set(D) == set(E), 'key 集合变化'
    rest = [k for k in E if D[k] == E[k]]
    print(f'写回完成：{len(out)} bytes / 裸 LF {chk.count(chr(10).encode())} / 值仍同英文 {len(rest)} 个')
    return 0


if __name__ == '__main__':
    sys.exit(main())
