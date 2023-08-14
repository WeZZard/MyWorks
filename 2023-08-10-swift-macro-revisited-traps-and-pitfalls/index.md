---
title: "Swift Macro: Revisited - Traps and Pitfalls"
category: Programming
tags: [Swift, Macro]
isPublished: false
---

In the previous post, we learned the strengths that uniquely define Swift
Macro. In the meanwhile, the examples in it work "so far so good".
However, can we be confident and bold, implementing any Swift macros we
want now?

No.

The features that bring Swift Macro advantages also introduce traps and
pitfalls which could lead to dead ends. Next, I would like to show you
several ones that I've found and how to overcome them.

## Traps and Pitfalls

### Unexpected Control Flow Manipulation

The `#unwrap` example in the previous post shows that Swift Macro
expansion could involve **control flow manipulation** and
**lexical scope sharing**:

Before expansion:

```swift
func foo(_ bar: Int?) {
  #unwrapped(bar) {
    print(bar)
  }
}
```

After expansion:

```swift
func foo(_ bar: Int?) {
  // #unwrapped expansion began
  guard let bar = bar else {
    return
  }
  print(bar)
  // #unwrapped expansion ended
}
```

Since the `return` statement in the macro expansion which manipulates the
control flow is an intentional behavior, this would not make us surprised.
But what if we put this macro in a loop? Here is an example:

Before expansion:

```swift
func foo(_ bar: Int?) {
  for _ in 0..<10 {
    #unwrap(bar) {
      print(bar)
    }
  }
}
```

After expansion:

```swift
func foo(_ bar: Int?) {
  for _ in 0..<10 {
    // #unwrapped expansion began
    guard let bar = bar else {
      return
    }
    print(bar)
    // #unwrapped expansion ended
  }
}
```

From the example shown above, we can learn that if we pass a non-optional
value to `foo`, the `bar` would only be printed once. This is because the
`return` statement involved by the macro expansion would break the outer
loop.

However, the `#unwrap` macro's name only shows its purpose is to unwrap
optional values but not to return from a function. This might cause the
programmer that uses this macro to think the returning is an
**unintentional behavior**.

### Name Conflicts in Freestanding Macro

However, **unintentional control flow manipulation** is not only one
potential pitfall in the expansion that I gave for the `#unwrap` macro.
One more pitfall here is that the `bar` variable was re-bound by the
`#unwarp` macro after the macro was expanded. Let's continue to examine
the expansion result of the previous example:

```swift
func foo(_ bar: Int?) {
  // #unwrapped expansion began
  guard let bar = bar else {
    return
  }
  print(bar)
  // #unwrapped expansion ended
}
```

This brought variable name shadowing where the `guard let bar: Int`
shadows the argument `_ bar: Int?`. In the case of `#unwrap`, the variable
name shadowing is trivial because it is an intentional behavior. However,
shadowing variables other than the `Optional`s could be considered as
unrecommended practice in real-world programming -- in fact, that would
not be compiled in Swift. As I concluded before, freestanding Swift macro
expansions involve lexical scope sharing with the applied site. This
enables potential variable shadowing in macro expansions. Here is a
contrived example, the variable name `updater` is shadowed due to the
macro expansion:

Before expansion:

```swift
func foo(_ bar: Int?) {
  let updater = Updater()
  #unwrap(fee, foe, fum) {
    let updater = Updater()
    print(bar)
    updater.update()
  }
  print(updater.description)
}
```

After expansion:

```swift
func foo(_ bar: Int?) {
  // `updater` defined the first time
  let updater = Updater()
  // #unwrap expansion began
  guard let bar else {
    return
  }
  // `updater` defined the second time
  let updater = Updater()
  print(bar)
  updater.update()
  // #unwrap expansion ended
  print(updater.description)
}
```

With a clean build in Xcode, you could find this example could not be
compiled:

TODO: A figure shows the compilation failure for the code above

### Name Conflicts in Attached Macro

Potential name conflicts not only be possible when freestanding macros
meet functions but also be possible when attached macros meet type
declarations. Let's recall the expansion result of the `@COW` macro
example in the previous post:

```swift
@COW
struct User {

  // @COW expansion began
  private class Storage {

    var name: String

    // other properties ...

  }

  private var _$storage: Storage

  private func makeStorageUniqueIfNeeded() {
    if !isKnownUniquelyReferenced(&_$storage) {
      _$storage = Storage(name: name, ...)
    }
  }

  init(name: String, ...) {
    self._storage = Storage(name: name, ...)
  }
  // @COW expansion ended

  // @COW expansion began
  @COWIncluded(storage: _$storage)
  // @COW expansion ended
  var name: String {
    // @COWIncluded expansion began
    get { return _$storage.name }
    set {
      makeStorageUniqueIfNeeded()
      _$storage.name = newValue
    }
    // @COWIncluded expansion ended
  }

}
```

You may have noticed that there is a member added in the expansion that is
named with a pattern that has a `_$` prefix.

```swift
  private var _$storage: Storage
```

This is a naming convention that I learned from Apple's implementation of
the macros in Swift Observation and SwiftData which keeps the
implementation details of an attached macro from the programmer's
unintentional access. However, this does not protect those members from
unintentional redeclaration or access brought by other macros -- there
could be other macros that are applied by the programmer which add members
with duplicate names or misuse members added by other macros.

For example, let's say there was a macro called `@DictionaryLike` which
makes the applied type behaves like a dictionary by adding a pair of
`subscript` getter and setter. Then we apply `@DictionaryLike` on the
`User` struct we used in the `@COW` macro example:

```swift
@DictionaryLike
struct User {

  // Other contents ...

}
```

The `@DictionaryLike` could be expanded as the following code:

```swift
@DictionaryLike
struct User {

  // Other contents ...

  // @DictionaryLike exapnsion began
  var _$storage: [String : Any] = [:]

  subscript(_ key: String) -> Any? {
    get { return _$storage[key] }
    set { _$storage[key] = newValue }
  }
  // @DictionaryLike exapnsion ended

}
```

Once we stack up `@COW` and `@DictionaryLike` together on the same type,
then there come to the situation that both `@COW` and `@DictionaryLike`
adds a member named `_$storage` to the applied type.

```swift
@COW
@DictionaryLike
struct User {

  // Other contents ...

  // Brought by @COW's expansion
  var _$storage: Storage

  // Brought by @DictionaryLike's expansion
  var _$storage: [String : Any] = [:]

}
```

This obviously would not get compiled in Swift because Swift does not
allow overloads on properties. We would get the “invalid redeclaration of
a variable” error again.

TODO: Compilation failure of the code above

### Name Conflicts for Unique Language Structures

The name collision is not the only pitfall of Swift Macro. Some language
structures in Swift are unique under the superstructure. This means when
multiple macros try to generate the same substructure in the same
superstructure, the code comes to be uncompilable.

We can contrive this by starting from the previous `@DictionaryLike`
example. Let's consider there is an attached accessor macro called
`@UseDictionaryStorage` which generates `get` and `set` accessor for the
attached property. The getter and setter forward access to the storage
which is brought by the expansion of `@DictionaryLike`.

Before macro expansion:

```swift
@COW
@DictionaryLike
struct User {
  
  @UseDictionaryStorage
  var info: [String : Any]?

}
```

After macro expansion:

```swift
@COW
@DictionaryLike
struct User {
  
  @UseDictionaryStorage
  var info: [String : Any]? {
    // @UseDictionaryStorage exapnsion began
    get {
      return _$storage["info"] as? [String : Any]?
    }
    set {
      _$storage["info"] = newValue
    }
    // @UseDictionaryStorage exapnsion ended
  }

}
```

However, that's oversimplified what happened. The real expansion result
with `@COW` macro is:

```swift
@COW
@DictionaryLike
struct User {
  
  @UseDictionaryStorage
  @COWIncluded
  var info: [String : Any]? {
    // @COWIncluded expansion began
    get {
      _$storage.info
    }
    set {
      makeStorageUniqueIfNeeded()
      _$storage.info = newValue
    }
    // @COWIncluded expansion ended
    // @UseDictionaryStorage exapnsion began
    get {
      return _$storage["info"] as? [String : Any]?
    }
    set {
      _$storage["info"] = newValue
    }
    // @UseDictionaryStorage exapnsion ended
  }

}
```

We can observe that two `get` and `set` accessors are generated under the
`info` property. Since the Swift programming language grammar only allows
one `get`/`set` accessor in one property, this expansion would lead to
incorrect syntax in Swift and ultimately make the code not compile.

TODO: Previous code snippet does not compile

### Name Conflicts by Referring Declarations in Other Frameworks

Since we've learned several cases of potential name conflicts caused by
adding declarations, you might think that the list of name conflicts is
ended up.

But no. Name conflicts not only could be brought by declaring a variable,
a member of a type or an accessor, but also could be brought by referring
declarations in other frameworks. I would like to show you how we could
be cornered into this case by refactoring the `@COW` macro example.

The `@COW` macro example I've shown above is a naïve implementation. We
can extract the `makeStorageUniqueIfNeeded` function to a type called
`Box` that is bundled with the library containing the `@COW` macro. To
streamline the use of this type in macro expansions, we could make it a
property wrapper.

```swift
@propertyWrapper
public struct Box<Contents> {
  
  private class Heap {
    
    var contents: Contents
    
    init(contents: Contents) { self.contents = contents }
    
  }
  
  private var heap: Heap
  
  public init(wrappedValue: Contents) {
    heap = Heap(contents: wrappedValue)
  }
  
  public var wrappedValue: Contents {
    get { heap.contents }
    set {
      makeUniqueHeapIfNeeded()
      heap.contents = newValue
    }
  }
  
  private mutating func makeUniqueHeapIfNeeded() {
    guard !isKnownUniquelyReferenced(&heap) else { return }
    heap = Heap(contents: heap.contents)
  }
  
}
```

Then we can attach `@Box` in the `_$storage` property brought by the macro
expansion such that we can eliminate generating the
`makeStorageUniqueIfNeeded` function in place. This reduces redundant
generated code and increased the speed of compilation.

```swift
@COW
struct User {

  // @COW expansion began
  private struct Storage {

    var name: String

    // other properties ...

  }

  @Box
  private var _$storage: Storage

  init(name: String, ...) {
    self._$storage = Storage(name: name, ...)
  }
  // @COW expansion ended

  // @COW expansion began
  @COWIncluded(storage: _$storage)
  // @COW expansion ended
  var name: String {
    // @COWIncluded expansion began
    get { return _$storage.name }
    set { _$storage.name = newValue }
    // @COWIncluded expansion ended
  }

}
```

However, the type name `Box` may be ambiguous -- there could be other
frameworks that also have a type called `Box`. When ambiguity is
encountered, the code would come to be uncompilable.

TODO: Figure about the ambiguity of resolving `Box`

### Semantics Conflicts

In the `@DictionaryLike` macro example, we've learned that accessor macro
would affect each other. However, this is not the only potential pitfall
brought by accessor macros: some language features could also be
interfered with by attached macros. Look at the following example: a
property wrapper makes the code not compiled by being attached to a stored
property in a struct applied `@COW` macro.

Before the expansion:

```swift
@propertyWrapper
struct Capitalized {
  
  var wrappedValue: String {
    didSet {
      wrappedValue = wrappedValue.capitalized
    }
  }
  
}

@COW
struct User {
  
  @Capitalized
  var name: String = ""
  
}
```

After the expansion:

```swift
@COW
struct User {
  
  @COWIncluded
  @Capitalized
  var name: String = "" {
    get {
      return _$storage.name
    }
    set {
      makeStorageUniqueIfNeeded()
      _$storage.name = newValue
    }
  }

  // ...

}
```

We got this expansion result because the property wrapper "expansion"
happens later than the macro expansion. With this result, the
`@Capitalized` property wrapper is still attached to the `name` variable
but the variable is changed from a stored property into a computed
property due to the macro expansion. Eventually, we would get an error
diagnosed by the compiler:

> Property wrapper cannot be applied to a computed property

TODO: Replace with Xcode screenshot

This does not only happen along with property wrappers, the `lazy` keyword
could also lead to the same dead end.

```swift
@COW
class User {
  
  lazy var name: String = { "Jane Doe" }()
  
}
```

```swift
@COW
class User {
  
  @COWIncluded
  lazy var name: String = { "Jane Doe" }() {
    get {
      return _$storage.name
    }
    set {
      makeStorageUniqueIfNeeded()
      _$storage.name = newValue
    }
  }

  // ...

}
```

TODO: Replace with Xcode screenshot

With these examples, we can learn that the expansion of a Swift macro
could change the semantics of the source code. This could lead to a
semantics conflict and ultimately make the expansion result not compile.

## Solutions

In the previous section, we've learned typical pitfalls that could be
found in implementing a Swift macro. These pitfalls could be generalized
and categorized into several kinds:

1. The macro expansion occupies non-unique names like `_$storage`.
2. The macro expansion occupies unique names like `get` or `set`.
3. The macro apply site also utilizes unstoppable source code generation
  language features like property wrapper or `lazy` keyword.
4. The macro expansion refers to non-standard-library types, functions or
  variables.

All these pitfalls could be overcome by a set of methods that I called
gradual control over code generation -- which was derived from the concept
of progressive disclosure in API design and the concept of gradual typing.

1. The first level of code generation control is no control which can be
  achieved by using `MacroExpansionContext.makeUniqueName(_:)`.
2. The second level of code generation control is that the code generation
  should be stopped when the name is occupied by the programmer's code.
3. The third level of code generation control is that the programmer can  
  explicitly turn off it.
4. The fourth level of code generation control is that the programmer can
  explicitly customize the name used for code generation.
5. Use the fully-qualified name when referring to non-standard-library
  types, functions or variables.

Let's see how this set of methods works in real examples:

For the first kind of pitfall, we have seen enough examples in the
previous section.

TODO: TBD

The second kind of pitfall could appear when there is an open-source
version of Swift Observation that copied the source code of Swift
Observation but renamed the `@Observable` macro into `@MyObservable` and a
programmer wants to apply both `@Observable` and `@MyObservable` on a
single class:

```swift
@Observable
@MyObservable
class Model {

  var name: String

}
```

This would be expanded into:

```swift
@Observable
@MyObservable
class Model {

  @ObservationTracked
  @MyObservationTracked
  var name: String {
    init(initialValue) initializes (_name) {
      _name = initialValue
    }
    get {
      access(keyPath: \.name)
      return _name
    }
    set {
      withMutation(keyPath: \.name) {
        _name = newValue
      }
    }
    init(initialValue) initializes (_name) {
      _name = initialValue
    }
    get {
      access(keyPath: \.name)
      return _name
    }
    set {
      withMutation(keyPath: \.name) {
        _name = newValue
      }
    }
  }

}
```

Attention, this is not a joke. Since Swift Observation is the killer app
of Swift Macro and Swift Observation requires the minimum deployment
target set to iOS 17.0. As a real example, the community has already built
OpenCombine to use the APIs in Combine on lower versions of iOS.

---

- When the macro expansion occupies non-unique names
  - Compiler-generated names do not make trouble in debugging
    - makeUniqueName
  - Compiler-generated names make trouble in debugging
    - Stop generation when the name was used by the programmer
    - Programmers can explicitly stop the code generation
    - Customizable names
  - Consider moving to a framework type and access with a full-qualified
    name
- The macro expansion occupies unique names (`willSet`, `didSet`)
  - Let the user be able to stop code generation
- The macro expansion refers to non-standard-library names
  - Use full-qualified names

---

### Beyond the Limitations of Freestanding Macro

To fix this potential variable name shadowing for freestanding macros, we
could create a closure and execute it immediately in place:

```swift
func foo(_ bar: Int?) {
  // `updater` defined the first time
  let updater = Updater()
  // #unwrap expansion began
  guard let bar else {
    return true
  }
  { (bar: Int) -> Void in
    // `updater` defined the second time
    let updater = Updater()
    print(bar)
    updater.update()
  }(bar)
  // #unwrap expansion ended
  print(updater.description)
}
```

The manually created closure introduced a lexical scope for the embraced
contents of the macro expansion which prevented the variable name from
being shadowed in previous examples.

But once the body of the closure contains control flows, the closure body
would not get inlined by the optimizer in its performance inlining pass.
This could leave the body of the closure out of the local analysis and
optimization of the macro's apply site. In some cases, this also means to
larger code size. To get rid of this situation, we could use the local
function instead of closure and attribute the local function as
`@inline(__always)`.

```swift
func foo(_ bar: Int?) {
  // `updater` defined the first time
  let updater = Updater()
  // #unwrap expansion began
  guard let bar else {
    return true
  }
  @inline(__always)
  func unwrapped(bar: Int) -> Void {
    // `updater` defined the second time
    let updater = Updater()
    print(bar)
    updater.update()
  }
  unwrapped(bar)
  // #unwrap expansion ended
  print(updater.description)
}
```

However, we can quickly find that once the `#unwrap` macro is applied
twice in a single function, the `unwrapped` function would collide. This
could be solved by using `MacroExpansionContext.makeUniqueName(_:)` to
generate a unique name for the `unwrapped` function.

### Beyond the Limitations of Attached Macros

The issues of the attached macros I shown above are obviously of two
categories:

- Name conflicts brought by sharing the "namespace".
- Semantics conflicts brought by semantics change due to macro expansion.

Dealing with name conflicts brought by the attached macro seems not
difficult since we've done that with freestanding macros. But how to deal
with semantics conflicts?

In the real world, one single macro author cannot predict what names all
other macro authors could pick, and in the real world, invariant semantics
should not be a property of Swift macro expansion, because it could
decrease the flexibility of the language feature. Based on this point, I
concluded a concept to deal with both two issues: gradual control over
code generation -- which is derived from the concept of progressive
disclosure in API design and the concept of gradual typing.

Just let me show you what is "gradual control over code generation" by
example.

We still use the `@COW` example here. The conflicts could be resolved if
we can control `@COW` to generate member names at the programmer's will.
What might be something new to you is this could be done by macro
overloading:

```swift
@COW(storageName: "_$cowStorage")
@DictionaryLike(storageName: "_$dictStorage")
struct User {

  // ...

  // Brought by @COW's expansion
  var _$cowStorage: Storage

  // Brought by @DictionaryLike's expansion
  var _$dictStorage: [String : Any] = [:]

}
```

In the example above, we overloaded `@COW` and `@DictionaryLike` macros to
have a parameter called `storageName` to specify the variable name of the
generated storage of each macro.

`MacroExpansionContext.makeUniqueName(_:)` is not recommended here because
the name generated by `MacroExpansionContext.makeUniqueName(_:)` with real
running compiler instance is a mangled string, which is OK for
freestanding macros debugging but may introduce troubles into attached
macros debugging.

TODO: A real example of generated unique name

But what if there are potential conflicts of
`makeStorageUniqueIfNeeded()`? I mean what if there are two macros

There are the principles that we can learn from what we've done:

1. For generated properties and non-standard library typed generated
   functions brought by attached member macros, we should enable
   programmers to optionally customize its name.
2. For standard library typed generated functions brought by attached
   member macros, we should stop code generation if there has already been
   one.
3. For attached member macros that generate members in type declarations,
   we should always offer an option to disable the code generation for
   specified members by applying an attached member attribute macro.

All these principles fall into a goal that to enable the programmers to
resolve conflicts by themselves. Again,
`MacroExpansionContext.makeUniqueName(_:)` is not recommended here because
it introduces unreadable names which may interfere with debugging.

These principles could also be used for resolving conflicts brought by
semantics changes due to macro expansion:

```swift
import Observation

@Observable
class Model {
  
  // Application of principle 3
  // Resolve conflicts by hand
  @ObservationIgnored
  @Capitalized
  var _name: String = ""
  
  var name: String {
    get {
      access(keyPath: \.name)
      return _name
    }  
    set {
      withMutation(keyPath: \.name) {
        _name = newValue
      }
    }
  }
  
}
```

## Future Directions

---

- Further directions:
  - More IDE collaboration: syntax highlighting

---

We've understood the nature of Swift macro by learning so much more.
But are these limitations still will be there in the future?

From what I've learned, my answer is yes. Because what brings Swift Macro
advantages also brings limitations. These limitations are also a part of
the essence of Swift macro.

But there are several pieces of information that you might not know about
which I collected from Swift evolution proposals and the latest source
code changes in the Swift repository.

### Init Accessor

The `init` accessor is introduced to eliminate the limitation that the
`@Observable` macro Swift Observation requires properties to have initial
values. This change has been bundled with Xcode 15 beta 4:

```swift
import Observation

@Observable
class Model {

  var foo: Int

}
```

The code above is not compiled before Xcode 15 beta 4, but will be
expanded into the following code after it:

```swift
import Observation

@Observable
class Model {

  var _foo: Int

  var foo: Int {
    init(initialValue) initializes(_foo) {
      _foo = initialValue
    }
    get {
      return _foo
    }
    set {
      _foo = newValue
    }
  }
  
  // ...

}
```

### Macro Argument Type Info

The proposal SE-0382 Expression Macros was written that:

> The arguments to a macro are fully type-checked before the macro
> implementation is invoked. However, information produced while
> performing that type-check is not provided to the macro, which only gets
> the original source code. In some cases, it would be useful to also have
> information determined during type checking, such as the types of the
> arguments and their subexpressions, the full names of the declarations
> referenced within those expressions, and any implicit conversions
> performed as part of type checking.

And there is also a comprehensive example in the proposal which is there
could be an `#assert` macro

```swift
#assert(Color(parsing: "red") == .red)
```

That can be expanded into:

```swift
{
  let _unique1 = Color(parsing: "red")
  let _unique2 = .red
  if !(_unique1 == _unique2) {
    fatalError("assertion failed: \(_unique1) != \(_unique2)")
  }
}()
```

Since `let _unique2 = .red` does not have type annotation, the expanded
code would not get compiled. By providing type info for the macro
arguments, specifically about the 'Color' type in this example,
this can be expanded as follows:

```swift
{
  let _unique1: Color = Color(parsing: "red")
  let _unique2: Color = .red
  if !(_unique1 == _unique2) {
    fatalError("assertion failed: \(_unique1) != \(_unique2)")
  }
}()
```

This time the code would get compiled.

But porting Swift type info which retained by the compiler that
implemented in C++ to Swift and make the programming interface to be
simple and ergonomic to most Swift developers is quite a challenging task.
Because there are a lot of detailed information about a type derived by
the compiler which is used for SIL generation and upcoming optimizations.
Macro authors should not care about them.
