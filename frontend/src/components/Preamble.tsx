export function Preamble() {
  return (
    <p className="mb-8 text-xs text-muted">
      <a href="/subscribe" className="text-accent hover:text-accent-hover">Subscribe</a>
      {" \u00b7 "}
      <a href="https://github.com/savannahostrowski/coredispatch.xyz/issues/new?template=submit-link.yml" className="text-accent hover:text-accent-hover">Submit a link</a>
      {" \u00b7 "}
      <a href="https://devguide.python.org/" className="text-accent hover:text-accent-hover">Contribute to CPython</a>
    </p>
  );
}
