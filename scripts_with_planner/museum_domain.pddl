(define (domain museum_guide)
    (:requirements :strips)
    (:predicates (at ?r ?l1)  (connected ?l1 ?l2)  (entrance ?e)  (has_painting ?l1 ?p)  (location ?l1)  (paints ?p)  (queue ?p)  (robot ?r)  (visited ?p))
    (:action is_queue
        :parameters (?r ?l1 ?l2 ?p)
        :precondition (and (robot ?r) (location ?l1) (paints ?p) (or (location ?l2) (entrance ?l2)) (connected ?l1 ?l2) (not (visited ?p)) (queue ?p) (at ?r ?l1) (has_painting ?l1 ?p))
        :effect (and (at ?r ?l2) (not (at ?r ?l1)) (not (queue ?p)) (visited ?p))
    )
     (:action move
        :parameters (?r ?l1 ?l2)
        :precondition (and (robot ?r) (or (location ?l1) (entrance ?l1)) (or (location ?l2) (entrance ?l2)) (at ?r ?l1) (connected ?l1 ?l2))
        :effect (and (at ?r ?l2) (not (at ?r ?l1)))
    )
     (:action visit
        :parameters (?r ?l1 ?p)
        :precondition (and (robot ?r) (location ?l1) (paints ?p) (not (visited ?p)) (not (queue ?p)) (at ?r ?l1) (has_painting ?l1 ?p))
        :effect (visited ?p)
    )
)