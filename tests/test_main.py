from statex import def_sx, sx, use_state
from statex.statex import set_sx
from tests.helpers import ChangeTracker
import typing as t


def test_object():
    trk = ChangeTracker()

    class State:
        f1: str = "val1"
        f2: int = 1

    st = use_state(State)
    assert st.f1 == "val1"
    assert st.f2 == 1
    trk.track("f1", sx(st).f1)
    trk.track("f2", sx(st).f2)
    # f1
    st.f1 = "val2"
    trk.assert_set("f1", "val2")
    # f2
    st.f2 = 2
    trk.assert_set("f2", 2)


def test_list():
    trk = ChangeTracker()

    class State:
        li: list[int] = []

    st = use_state(State)
    trk.track("li", sx(st).li)
    st.li.append(1)
    trk.assert_set("li", [1])


def test_dict():
    trk = ChangeTracker()

    class State:
        di: dict[str, str] = {}

    st = use_state(State)
    trk.track("di", sx(st).di)
    st.di["a"] = "1"
    trk.assert_set("di", {"a": "1"})


def test_list_obj():
    trk = ChangeTracker()

    class Child:
        f1: str = "val1"
        f2: int = 1

    class State:
        def __init__(self) -> None:
            self.li: list[Child] = []

    st = use_state(State)
    st.li.append(Child())

    trk.track("li", sx(st).li)
    trk.track("li[0].f1", sx(st.li[0]).f1)
    st.li[0].f1 = "val2"
    trk.assert_set("li[0].f1", "val2")
    st.li.pop()
    trk.assert_set("li", [])


def test_calc():
    trk = ChangeTracker()

    class State:
        li: list[int] = []

        @def_sx("li")
        def count(self):
            return len(self.li)

    st = use_state(State)
    trk.track("count", sx(st).count)
    st.li.append(1)
    trk.assert_set("count", 1)
    st.li.append(2)
    trk.assert_set("count", 2)


def test_calc_with_arg():
    trk = ChangeTracker()

    class State:
        li: list[int] = []

        @def_sx("li")
        def count_with(self, x: int = 1):
            return x + len(self.li)

    st = use_state(State)

    xx = sx(st).count_with(x=5)
    xx.get()

    trk.track("count_with_5", sx(st).count_with(x=5))
    trk.track("count_with_7", sx(st).count_with(x=7))
    st.li.append(1)
    trk.assert_set("count_with_5", 6)
    trk.assert_set("count_with_7", 8)
    st.li.append(2)
    st.li.append(3)
    trk.assert_set("count_with_5", 8)
    trk.assert_set("count_with_7", 10)


def test_source():
    trk = ChangeTracker()

    class State:
        f1: str = "val1"

    st = use_state(State)
    source = object()
    trk.track("f1", sx(st).f1)

    # st.f1 = "val2"
    set_sx(sx(st).f1, "val2", src=source)

    trk.assert_set("f1", "val2", source=source)


def test_performance():
    import timeit

    counter = 0
    loops = 100000

    def f_with():

        class State:
            f1: int = -1

        st = use_state(State)
        f1 = sx(st).f1

        def on_change(src: t.Any):
            nonlocal counter
            counter += f1.get()

        sx(st).f1.on_change(on_change)

        for i in range(loops):
            st.f1 = i

    def f_without():
        nonlocal counter

        class State:
            f1: int = -1

            def __setattr__(self, name: str, value: t.Any) -> None:
                if name == "f1":
                    nonlocal counter
                    counter += value
                    return
                super().__setattr__(name, value)

        st = State()

        for i in range(loops):
            st.f1 = i

    elapsed_time = timeit.timeit("f_with()", globals=locals(), number=1)
    print(f"Executed with state, counter:{counter} time:{elapsed_time:.5f} seconds")
    counter = 0
    elapsed_time = timeit.timeit("f_without()", globals=locals(), number=1)
    print(f"Executed w/o state, counter:{counter} time:{elapsed_time:.5f} seconds")
