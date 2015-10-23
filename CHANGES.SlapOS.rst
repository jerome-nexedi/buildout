2.5.2+slapos004
---------------

Rebase to refresh some patches and fix commits that were wrongly cherry-picked
from Nexedi 1.x branch. Changed:

- Give the same permission but write as owner to group and other.
- Make buildout.rmtree working with symlink as a path argument.
- Add referred parts' hash strings in __buildout_signature__, that invokes
  rebuild of a part when one of its (recursive) dependencies are modified.
- Write .installed.cfg only once, in safe way and only if there's any change.
- Escape $$ character to $.

2.5.2+slapos003
---------------

- Expand sys.path when PYTHONEXTRAPATH is present for develop.

2.5.2+slapos002
---------------

- Fix a bug where slapos.libnetworkcache is lost when buildout script
  is upgraded.

2.5.2+slapos001
---------------

- Rebase with 2.5.2
- In verbose mode, save .installed.cfg each time a part is installed.

2.5.1+slapos001
---------------

- Rebase with 2.5.1

2.5.0+slapos001
---------------

- Rebase with 2.5.0
- Fix a bug in $$ escape handling.

2.4.7+slapos001
---------------

- Rebase with 2.4.7.
- Support Python 3.

2.4.5+slapos001
---------------

- Support ${:_profile_base_location_}.
- Support on the fly patches in easy_install.
- Merge PYTHONEXTRAPATH value into PYTHONPATH in easy_install so that we can
  use some eggs that are required to build an egg.
- Support network cache in download.py and easy_install.py
- Cache downloaded data in zc/buildout/buildout.py:_open() in memory
  to accelerate remote extends.
- Give the same permission but write as owner to group and other.
- Make buildout.rmtree working with symlink as a path argument.
    https://bugs.launchpad.net/zc.buildout/+bug/144228
- Respect specified versions of initial eggs in bootstrap.
- Keep develop-eggs directory in bootstrap.
- Add referred parts' hash strings in __buildout_signature__, that invokes
  rebuild of a part when one of its (recursive) dependencies are modified.
- Allow assigning non-string values to section keys. Restricted to selected
  python base types.
- Write .installed.cfg only once, in safe way and only if there's any change.
- Put only one [buildout] section in .installed.cfg.
- Escape $$ character to $.
- Compare Options with sorted result, if possible.
- Add '--dry-run' option.
- Add '--skip-signature-check' option.

not applied (still required?)
-----------------------------

- 83fc3a2 Always use build() in easy_install.py to install eggs.
  (it's not required if the commit below is not applied, I guess)
- b7cd5ca Include '.postN' in generated egg's version so that version pinning with 'N.N.N.postN' works.
- 1761c65 Workaround M2Crypto bug of https redirection.
