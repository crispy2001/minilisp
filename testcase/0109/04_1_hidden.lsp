(print-bool #f)
(print-bool #t)

(print-bool (or #t #t))
(print-bool (or #f #t))

(print-bool (not #f))
(print-bool (not #t))

(print-bool (and #t #t))
(print-bool (and #f #t))

