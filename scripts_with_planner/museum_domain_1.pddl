(define (domain museum_guide)
    (:requirements :strips)
    (:predicates (at ?r ?l1)  (connected ?l1 ?l2)  (entrance ?e)  (location ?l1)  (robot ?r))
    (:action move
        :parameters (?r ?l1 ?l2)
        :precondition (and (robot ?r) (or (location ?l1) (entrance ?l1)) (or (location ?l2) (entrance ?l2)) (at ?r ?l1) (connected ?l1 ?l2))
        :effect (and (at ?r ?l2) (not (at ?r ?l1)))
    )
)