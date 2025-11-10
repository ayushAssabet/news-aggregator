from utils.dedupe import fingerprint

def test_fingerprint_changes_with_title_and_url():
    fp1=fingerprint('Hello World','https://example.com?a=1&utm_source=foo')
    fp2=fingerprint('Hello  World ','https://example.com?a=1')
    assert fp1==fp2
    assert len(fp1)==64
